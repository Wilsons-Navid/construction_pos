from database.database import DatabaseUtils

TRANSLATIONS = {
    'en': {
        'customer': 'Customer',
        'tax_rate': 'Tax Rate (%)',
        'tax_amount': 'Tax Amount',
        'total': 'Total',
        'total_sales': 'Total Sales',
        'revenue': 'Revenue',
        'low_stock': 'Low Stock Items',
        'language': 'Language',
        'theme': 'Theme',
        'settings': 'Settings',
        'users': 'Users',
        'preferences': 'Preferences',
        'username': 'Username',
        'password': 'Password',
        'add_user': 'Add User',
        'save_preferences': 'Save Preferences',
        'user_added': 'User added successfully',
        'pos': 'Point of Sale',
        'inventory': 'Inventory',
        'reports': 'Reports',
        'customers': 'Customers',
    },
    'fr': {
        'customer': 'Client',
        'tax_rate': 'Tax (%)',
        'tax_amount': 'Montant Taxe',
        'total': 'Total',
        'total_sales': 'Ventes',
        'revenue': 'Revenu',
        'low_stock': 'Stock Faible',
        'language': 'Langue',
        'theme': 'Thème',
        'settings': 'Paramètres',
        'users': 'Utilisateurs',
        'preferences': 'Préférences',
        'username': 'Nom d\u2019utilisateur',
        'password': 'Mot de passe',
        'add_user': 'Ajouter',
        'save_preferences': 'Enregistrer',
        'user_added': 'Utilisateur ajouté',
        'pos': 'Point de Vente',
        'inventory': 'Inventaire',
        'reports': 'Rapports',
        'customers': 'Clients',
    },
}


def translate(key: str) -> str:
    """Translate a key based on current language setting."""
    lang = DatabaseUtils.get_setting_value('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
