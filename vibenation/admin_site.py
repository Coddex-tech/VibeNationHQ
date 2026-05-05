from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
from io import BytesIO
import base64
from django.utils.safestring import mark_safe
# FOR STAFF PORTAL
from django.contrib.admin import AdminSite
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect

# --- THE BOSS PORTAL (SUPERADMIN ONLY) ---
from django.contrib.admin import AdminSite
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django_otp.admin import OTPAdminSite

# --- THE BOSS PORTAL ---
class MasterAdminSite(OTPAdminSite):
    site_header = "VibeNationHQ Boss Portal"
    site_title = "Master Portal"
    enable_nav_sidebar = True 

    def index(self, request, extra_context=None):
        # Using first name for the Boss dynamic greeting
        name = "Boss"
        self.index_title = f"Welcome, {name}"
        return super().index(request, extra_context=extra_context)

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def login(self, request, extra_context=None):
        if request.user.is_authenticated and not request.user.is_superuser:
            logout(request)
            messages.error(request, "Access Denied: Boss Portal only.")
            return redirect('.')
        return super().login(request, extra_context)
    
    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request, app_label)
        
        my_order = {
            "news": 1,
            "music": 2,
            "ads": 3,
            "auth": 4,
            "admin_interface": 5,
        }
        
        app_list = sorted(
            app_dict.values(),
            key=lambda x: my_order.get(x['app_label'], 99)
        )

        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        return app_list

# Initialize the Boss Admin
admin_site = MasterAdminSite(name='admin_site')


# --- THE STAFF PORTAL ---
class StaffAdminSite(AdminSite):
    site_header = "VibeNationHQ Staff Portal"
    site_title = "Staff Admin"
    enable_nav_sidebar = True

    def index(self, request, extra_context=None):
        name = request.user.username or request.user.first_name
        self.index_title = f"Welcome, {name}"
        return super().index(request, extra_context=extra_context)

    def has_permission(self, request):
        return request.user.is_active and request.user.is_staff and not request.user.is_superuser

    def login(self, request, extra_context=None):
        if request.user.is_authenticated and request.user.is_superuser:
            logout(request)
            messages.error(request, "Access Denied: Staff Portal only. Please use the Private URL")
            return redirect('.')   
        return super().login(request, extra_context)
    
    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request, app_label)
        
        my_order = {
            "news": 1,
            "music": 2,
            "ads": 3,
        }
        
        app_list = sorted(
            app_dict.values(),
            key=lambda x: my_order.get(x['app_label'], 99)
        )

        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        # Filter out sensitive internal apps for Staff
        # hidden_apps = ['otp_totp', 'otp_static', 'sites', 'admin_interface', 'auth']
        # app_list = [app for app in app_list if app['app_label'] not in hidden_apps]

        return app_list

# Initialize the Staff Admin
staff_admin_site = StaffAdminSite(name='staff_admin')

# Register TOTP Devices (Boss Only)
@admin.register(TOTPDevice, site=admin_site)
class TOTPDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'confirmed']
    search_fields = ['user__username']
    readonly_fields = ['display_qr_code'] # Add this!

    def display_qr_code(self, obj):
        if obj.pk:
            # This creates the link the phone app understands
            url = obj.config_url
            
            # This turns that link into a QR image
            img = qrcode.make(url)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return mark_safe(f'<img src="data:image/png;base64,{img_str}" width="200" height="200" />')
        return "Save the device first to see the QR code."
    
    display_qr_code.short_description = "Scan this with Authenticator App"