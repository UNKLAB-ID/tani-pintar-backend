"""Django Unfold admin interface configuration."""

UNFOLD = {
    # Site branding
    "SITE_TITLE": "Tani Pintar Admin",
    "SITE_HEADER": "Taniverse",
    "SITE_SUBHEADER": "Smart Farmer Platform",
    "SITE_URL": "/",
    # Interface behavior
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    # Site icon and logo
    # "SITE_ICON": {  # noqa: ERA001
    #     "light": lambda request: "/static/images/tani-pintar-icon-light.svg",  # noqa: E501, ERA001
    #     "dark": lambda request: "/static/images/tani-pintar-icon-dark.svg",  # noqa: E501, ERA001
    # },
    # "SITE_LOGO": {  # noqa: ERA001
    #     "light": lambda request: "/static/images/tani-pintar-logo-light.svg",  # noqa: E501, ERA001
    #     "dark": lambda request: "/static/images/tani-pintar-logo-dark.svg",  # noqa: E501, ERA001
    # },
    "SITE_SYMBOL": "eco",  # Icon from Material Design Icons
    # Login page image
    "LOGIN": {
        "image": lambda request: "/static/images/favicons/login.svg",
    },
    # Color scheme - Greenish theme matching #FDFDFD background
    "COLORS": {
        "font": {
            "subtle-light": "120 130 140",
            "subtle-dark": "160 170 180",
            "default-light": "85 95 105",
            "default-dark": "250 252 250",
            "important-light": "25 35 45",
            "important-dark": "253 253 253",
        },
        "primary": {
            "50": "248 254 249",
            "100": "236 253 243",
            "200": "209 250 229",
            "300": "167 243 208",
            "400": "110 231 183",
            "500": "52 211 153",  # Main greenish accent
            "600": "16 185 129",
            "700": "5 150 105",
            "800": "6 120 86",
            "900": "6 95 70",
            "950": "2 44 34",
        },
    },
    # Sidebar configuration
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": False,
                "items": [
                    {
                        "title": "Overview",
                        "icon": "agriculture",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": "User Management",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "people",
                        "link": "/admin/users/user/",
                    },
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": "/admin/auth/group/",
                    },
                ],
            },
            {
                "title": "Profiles & Accounts",
                "separator": True,
                "items": [
                    {
                        "title": "User Profiles",
                        "icon": "eco",
                        "link": "/admin/accounts/profile/",
                    },
                    {
                        "title": "Follow Relationships",
                        "icon": "nature_people",
                        "link": "/admin/accounts/follow/",
                    },
                    {
                        "title": "Verification Codes",
                        "icon": "verified",
                        "link": "/admin/accounts/verificationcode/",
                    },
                    {
                        "title": "Login Codes",
                        "icon": "local_florist",
                        "link": "/admin/accounts/logincode/",
                    },
                ],
            },
            {
                "title": "Location Data",
                "separator": True,
                "items": [
                    {
                        "title": "Countries",
                        "icon": "public",
                        "link": "/admin/location/country/",
                    },
                    {
                        "title": "Provinces",
                        "icon": "map",
                        "link": "/admin/location/province/",
                    },
                    {
                        "title": "Cities",
                        "icon": "location_city",
                        "link": "/admin/location/city/",
                    },
                    {
                        "title": "Districts",
                        "icon": "place",
                        "link": "/admin/location/district/",
                    },
                ],
            },
            {
                "title": "Social Media",
                "separator": True,
                "items": [
                    {
                        "title": "Posts",
                        "icon": "article",
                        "link": "/admin/social_media/post/",
                    },
                    {
                        "title": "Post Images",
                        "icon": "image",
                        "link": "/admin/social_media/postimage/",
                    },
                    {
                        "title": "Post Comments",
                        "icon": "comment",
                        "link": "/admin/social_media/postcomment/",
                    },
                    {
                        "title": "Post Views",
                        "icon": "visibility",
                        "link": "/admin/social_media/postview/",
                    },
                    {
                        "title": "Post Likes",
                        "icon": "thumb_up",
                        "link": "/admin/social_media/postlike/",
                    },
                    {
                        "title": "Comment Likes",
                        "icon": "favorite",
                        "link": "/admin/social_media/postcommentlike/",
                    },
                    {
                        "title": "Saved Posts",
                        "icon": "bookmark",
                        "link": "/admin/social_media/postsaved/",
                    },
                    {
                        "title": "Reports",
                        "icon": "report",
                        "link": "/admin/social_media/report/",
                    },
                ],
            },
            {
                "title": "AI & Analytics",
                "separator": True,
                "items": [
                    {
                        "title": "Disease Detection",
                        "icon": "local_florist",
                        "link": "/admin/thinkflow/",
                    },
                ],
            },
            {
                "title": "E-commerce",
                "separator": True,
                "items": [
                    {
                        "title": "Product Categories",
                        "icon": "category",
                        "link": "/admin/ecommerce/productcategory/",
                    },
                    {
                        "title": "Product Sub Categories",
                        "icon": "subdirectory_arrow_right",
                        "link": "/admin/ecommerce/productsubcategory/",
                    },
                    {
                        "title": "Products",
                        "icon": "grass",
                        "link": "/admin/ecommerce/product/",
                    },
                    {
                        "title": "Product Images",
                        "icon": "image",
                        "link": "/admin/ecommerce/productimage/",
                    },
                    {
                        "title": "Product Prices",
                        "icon": "price_change",
                        "link": "/admin/ecommerce/productprice/",
                    },
                    {
                        "title": "Units of Measure",
                        "icon": "straighten",
                        "link": "/admin/ecommerce/unitofmeasure/",
                    },
                    {
                        "title": "Shopping Cart",
                        "icon": "shopping_cart",
                        "link": "/admin/ecommerce/cart/",
                    },
                ],
            },
            {
                "title": "Vendors",
                "separator": True,
                "items": [
                    {
                        "title": "Vendors",
                        "icon": "storefront",
                        "link": "/admin/vendors/vendor/",
                    },
                ],
            },
            {
                "title": "Background Tasks",
                "separator": True,
                "items": [
                    {
                        "title": "Periodic Tasks",
                        "icon": "schedule",
                        "link": "/admin/django_celery_beat/periodictask/",
                    },
                    {
                        "title": "Interval Schedules",
                        "icon": "timer",
                        "link": "/admin/django_celery_beat/intervalschedule/",
                    },
                    {
                        "title": "Crontab Schedules",
                        "icon": "schedule_send",
                        "link": "/admin/django_celery_beat/crontabschedule/",
                    },
                    {
                        "title": "Solar Schedules",
                        "icon": "wb_sunny",
                        "link": "/admin/django_celery_beat/solarschedule/",
                    },
                    {
                        "title": "Clocked Schedules",
                        "icon": "alarm",
                        "link": "/admin/django_celery_beat/clockedschedule/",
                    },
                ],
            },
            {
                "title": "System",
                "separator": True,
                "items": [
                    {
                        "title": "Health Check",
                        "icon": "health_and_safety",
                        "link": "/health-check/",
                    },
                ],
            },
        ],
    },
    # Extensions for third-party integrations
    # "EXTENSIONS": {  # noqa: ERA001
    #     "modeltranslation": {  # noqa: ERA001
    #         "flags": {  # noqa: ERA001
    #             "en": "🇺🇸",  # noqa: ERA001
    #             "id": "🇮🇩",  # noqa: ERA001
    #         },
    #     },
    # },
    # Site dropdown for additional links
    "SITE_DROPDOWN": [
        {
            "title": "API Documentation",
            "link": "/api/docs/",
            "icon": "api",
        },
        {
            "title": "Health Check",
            "link": "/health-check/",
            "icon": "health_and_safety",
        },
    ],
}
