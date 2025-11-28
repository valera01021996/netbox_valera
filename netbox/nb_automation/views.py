import pandas as pd
import ipaddress
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from .forms import ExcelRegionImportForm

# NetBox/DCIM Region (NetBox 4.x)
from dcim.models.sites import Region, Site, Location
from dcim.models.racks import Rack
from dcim.models.devices import DeviceRole, Manufacturer, DeviceType, Platform, Device, Interface
from ipam.models.vlans import VLAN
from ipam.models.ip import IPAddress, Prefix
from tenancy.models import Tenant


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
        created_interfaces = 0
        created_vlans = 0
        created_ip_addresses = 0
        created_prefixes = 0
        created_tenants = 0
        created_rack_face = 0

        required_cols = {"Region", "Tenant", "Site", "Location", "Rack", "RackFace", "Role", "Manufacturer", "DeviceType", "Height", "Platform", "DeviceName", "Position", "InterfaceName", "VLAN", "IP", "Mask"}

        if not required_cols.issubset(df.columns):
            messages.error(self.request, f"File must include columns: {', ' .join(required_cols)}")
            return redirect(self.get_success_url())
        

        for _, row in df.iterrows():
            region_name = str(row["Region"]).strip()
            site_name = str(row["Site"]).strip()
            location_name = str(row["Location"]).strip()
            # rack_name = str(row["Rack"]).strip()


            raw_rack = str(row["Rack"]).strip()
            parts = raw_rack.split("-", 1)
            rack_name = parts[0].strip() if parts else raw_rack
            rack_u_height = None

            if len(parts) > 1:
                height_str = parts[1].strip()
                try:
                    rack_u_height = int(height_str)
                except ValueError:
                    messages.warning(self.request, f"Invalid U height for rack {raw_rack}: {height_str}")

            rack_face = str(row["RackFace"]).strip()
            device_role_name = str(row["Role"]).strip()
            manufacturer_name = str(row["Manufacturer"]).strip()
            device_type_name = str(row["DeviceType"]).strip()
            height = str(row["Height"]).strip()
            platform_name = str(row["Platform"]).strip()
            device_name = str(row["DeviceName"]).strip()
            position = str(row["Position"]).strip()
            interface_name = str(row["InterfaceName"]).strip()
            vlan_id = str(row["VLAN"]).strip()
            ip_a = str(row["IP"]).strip()
            mask = str(row["Mask"]).strip()
            tenant_name = str(row["Tenant"]).strip()
            
            if not region_name or not site_name or not location_name or not rack_name or not rack_face or not device_role_name or not manufacturer_name or not device_type_name or not height or not platform_name or not device_name or not position or not interface_name or not vlan_id or not ip_a or not mask or not tenant_name:
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

            
            tenant, created_tenant = Tenant.objects.get_or_create(
                name = tenant_name,
                defaults = {"slug": tenant_name.lower().replace(" ", "-")}
            )
            if created_tenant:
                created_tenants += 1

            rack, created_rack = Rack.objects.get_or_create(
                name = rack_name,
                site = site,
                location = location,
                defaults = {"u_height": rack_u_height} if rack_u_height else {}
            )

            if created_rack:
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
                tenant = tenant,
                rack = rack,
                face = rack_face,
                location = location,
                position = position,
                platform = platform
            )
            if created_device:
                created_devices += 1

            interface, created_interface = Interface.objects.get_or_create(
                name = interface_name,
                device = device,
                defaults = {
                    "type": "1000base-t",
                    "enabled": True
                }
            )
            if created_interface:
                created_interfaces += 1


            vlan, created_vlan = VLAN.objects.get_or_create(
                name = interface_name,
                vid = vlan_id,
                defaults = {"status": "active"}
            )
            if created_vlan:
                created_vlans += 1


            ip_address, created_ip_address = IPAddress.objects.get_or_create(
                address = ip_a + "/" + mask,
                defaults = {"status": "active"}
            )
            if created_ip_address:
                created_ip_addresses += 1

            interface.ip_addresses.add(ip_address)
            interface.save()

            ip_network = ipaddress.ip_network(f"{ip_a}/{mask}", strict=False)


            prefix, created_prefix = Prefix.objects.get_or_create(
                prefix = str(ip_network),
                vlan = vlan,
                defaults = {"status": "active"}
            )
            if created_prefix:
                created_prefixes += 1


            interface_name_lower = interface_name.lower()
            if interface_name_lower == "ssh":
                device.primary_ip4 = ip_address
                device.save()
            elif interface_name_lower == "ipmi":
                device.oob_ip = ip_address
                device.save()




        messages.success(
            self.request,
            f"Import finished."
            f"Regions added: {created_regions}, sites: {created_sites}, "
            f"locations: {created_locations}, racks: {created_racks}, "
            f"device roles: {created_device_roles}, "
            f"manufacturers: {created_manufacturers}, "
            f"device types: {created_device_types}, "
            f"platforms: {created_platforms}, "
            f"devices: {created_devices}, "
            f"interfaces: {created_interfaces}, "
            f"vlans: {created_vlans}, "
            f"ip addresses: {created_ip_addresses}, "
            f"prefixes: {created_prefixes}, "
            f"tenants: {created_tenants}."
        )



        return redirect(self.get_success_url())
