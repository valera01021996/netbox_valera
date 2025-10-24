from contextlib import nullcontext

import pandas as pd
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.text import slugify
from django.views.generic import FormView

from .forms import ExcelRegionImportForm

# NetBox/DCIM Region (NetBox 4.x)
from dcim.models.sites import Region, Site, Location
from dcim.models.racks import Rack
from dcim.models.devices import DeviceRole, Manufacturer, DeviceType, Platform, Device


class ExcelUploadView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = 'nb_automation/excel_upload.html'
    form_class = ExcelRegionImportForm
    permission_required = 'dcim.add_region'

    def get_success_url(self):
        return reverse('plugins:nb_automation:excel_upload')

    def form_valid(self, form):
        upload = form.cleaned_data['file']
        dry_run = form.cleaned_data['dry_run']

        # Базовые проверки
        if not upload.name.lower().endswith('.xlsx'):
            form.add_error('file', 'Waiting format file .xlsx')
            return self.form_invalid(form)

        try:
            # Читаем Excel целиком как строки, без индекса
            # engine='openpyxl' обязателен для .xlsx
            df = pd.read_excel(upload, engine='openpyxl', dtype=str)
        except Exception as e:
            form.add_error('file', f'Can not read Excel: {e}')
            return self.form_invalid(form)

        created_regions = 0
        created_sites = 0
        created_locations = 0
        created_racks = 0
        created_device_roles = 0
        created_manufacturers = 0
        created_device_types = 0
        created_platforms = 0
        created_devices = 0

        required_cols = {"Region", "Site", "Location", "Rack", "Role", "Manufacturer", "DeviceType", "Height", "Platform", "DeviceName", "Position"}

        if not required_cols.issubset(df.columns):
            messages.error(self.request, f"File must include columns: {', ' .join(required_cols)}")
            return redirect(self.get_success_url())
        

        for _, row in df.iterrows():
            region_name = str(row["Region"]).strip()
            site_name = str(row["Site"]).strip()
            location_name = str(row["Location"]).strip()
            rack_name = str(row["Rack"]).strip()
            device_role_name = str(row["Role"]).strip()
            manufacturer_name = str(row["Manufacturer"]).strip()
            device_type_name = str(row["DeviceType"]).strip()
            height = str(row["Height"]).strip()
            platform_name = str(row["Platform"]).strip()
            device_name = str(row["DeviceName"]).strip()
            position = str(row["Position"]).strip()


            if not region_name or not site_name or not location_name or not rack_name or not device_role_name or not manufacturer_name or not device_type_name or not height or not platform_name or not device_name or not position:
                messages.error(self.request, f"Row {row} is missing required fields. Please check the file and try again.")
                continue

            region, created = Region.objects.get_or_create(
                name = region_name,
                defaults = {"slug": region_name.lower().replace(" ", "-")}
            )
            if created:
                created_regions += 1

            site, created_site = Site.objects.get_or_create(
                name = site_name,
                region = region,
                defaults = {"slug": site_name.lower().replace(" ", "-")}
            )
            if created_site:
                created_sites += 1

            location, created_location = Location.objects.get_or_create(
                name = location_name,
                site = site,
                defaults = {"slug": location_name.lower()}
            )

            if created_location:
                created_locations += 1

            rack, created_racks = Rack.objects.get_or_create(
                name = rack_name,
                site = site,
                location = location
            )

            if created_racks:
                created_racks += 1


            device_role, created_device_role = DeviceRole.objects.get_or_create(
                name = device_role_name,
                defaults = {"slug": device_role_name.lower().replace(" ", "-"),
                "vm_role": False
                }
            )
            if created_device_role:
                created_device_roles += 1

            manufacturer, created_manufacturer = Manufacturer.objects.get_or_create(
                name = manufacturer_name,
                defaults = {"slug": manufacturer_name.lower().replace(" ", "-")}
            )
            if created_manufacturer:
                created_manufacturers += 1

            device_type, created_device_type = DeviceType.objects.get_or_create(
                model = device_type_name,
                manufacturer = manufacturer,
                defaults = {"slug": device_type_name.lower().replace(" ", "-"),
                "u_height": int(height)
                }
            )
            if created_device_type:
                created_device_types += 1

            platform, created_platform = Platform.objects.get_or_create(
                name = platform_name,
                defaults = {"slug": platform_name.lower().replace(" ", "-")}
            )
            if created_platform:
                created_platforms += 1

            
            device, created_device = Device.objects.get_or_create(
                name = device_name,
                device_type = device_type,
                role = device_role,
                site = site,
                rack = rack,
                location = location,
                position = position,
                platform = platform
            )
            if created_device:
                created_devices += 1

            
        messages.success(
            self.request,
            f"Import finished."
            f"Regions added: {created_regions}, sites: {created_sites}, "
            f"locations: {created_locations}, racks: {created_racks}, "
            f"device roles: {created_device_roles}, "
            f"manufacturers: {created_manufacturers}, "
            f"device types: {created_device_types}, "
            f"platforms: {created_platforms}."
        )



        return redirect(self.get_success_url())
