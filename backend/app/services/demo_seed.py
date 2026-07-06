# from ..models import Client, BusinessHours, MenuCategory, MenuItem
# from sqlalchemy.ext.asyncio import AsyncSession
# import re

# def get_cuisine_type(name: str) -> str:
#     name_lower = name.lower()
#     if any(k in name_lower for k in ["pizza", "italian", "pasta", "mario", "trattoria", "pizzeria"]):
#         return "italian"
#     elif any(k in name_lower for k in ["sushi", "japanese", "ramen", "tokyo", "sakura", "kyoto"]):
#         return "japanese"
#     elif any(k in name_lower for k in ["taco", "mexican", "burrito", "cantina", "mex", "el paso"]):
#         return "mexican"
#     elif any(k in name_lower for k in ["steak", "grill", "barbecue", "bbq", "smoke", "smokehouse", "ribs"]):
#         return "steakhouse"
#     elif any(k in name_lower for k in ["cafe", "coffee", "bakery", "bread", "sweet", "bites", "brew"]):
#         return "cafe"
#     return "family"

# def get_starter_menu_for(business_name: str):
#     cuisine = get_cuisine_type(business_name)
    
#     menus = {
#         "italian": [
#             {"name": "Margherita Pizza", "description": "Classic fresh mozzarella, tomato sauce, fresh basil, extra virgin olive oil.", "price": "12", "is_featured": True},
#             {"name": "Fettuccine Alfredo", "description": "Rich creamy butter and parmesan sauce over tender house-made fettuccine.", "price": "16", "is_featured": True},
#             {"name": "Bruschetta", "description": "Grilled bread rubbed with garlic, topped with diced tomatoes, fresh basil, olive oil.", "price": "8", "is_featured": False},
#             {"name": "Tiramisu", "description": "Espresso-soaked ladyfingers layered with whipped mascarpone cheese and cocoa.", "price": "9", "is_featured": False}
#         ],
#         "japanese": [
#             {"name": "Salmon Nigiri", "description": "Fresh slices of premium raw salmon served over seasoned sushi rice.", "price": "18", "is_featured": True},
#             {"name": "Tonkotsu Ramen", "description": "Rich pork bone broth, chashu pork, soft boiled egg, scallions, bamboo shoots, seaweed.", "price": "19", "is_featured": True},
#             {"name": "Vegetable Tempura", "description": "Crispy battered and deep-fried seasonal vegetables served with dipping sauce.", "price": "12", "is_featured": False},
#             {"name": "Matcha Ice Cream", "description": "Creamy traditional green tea flavored dessert.", "price": "7", "is_featured": False}
#         ],
#         "mexican": [
#             {"name": "Beef Tacos", "description": "Three corn tortillas filled with seasoned beef, cilantro, onions, and fresh lime.", "price": "11", "is_featured": True},
#             {"name": "Chicken Burrito", "description": "Large flour tortilla stuffed with grilled chicken, rice, beans, cheese, and salsa.", "price": "13", "is_featured": True},
#             {"name": "Guacamole & Chips", "description": "Freshly made avocado dip served with crispy house-made tortilla chips.", "price": "8", "is_featured": False},
#             {"name": "Churros", "description": "Fried dough pastry dusted with cinnamon sugar, served with chocolate sauce.", "price": "7", "is_featured": False}
#         ],
#         "steakhouse": [
#             {"name": "Ribeye Steak", "description": "12oz USDA Prime ribeye steak grilled to your liking, served with herb butter.", "price": "45", "is_featured": True},
#             {"name": "Smoked Brisket", "description": "Slow-smoked beef brisket, tender and juicy, glazed with house BBQ sauce.", "price": "28", "is_featured": True},
#             {"name": "Mac and Cheese", "description": "Creamy baked macaroni with a blend of cheddar, monterey jack, and breadcrumbs.", "price": "10", "is_featured": False},
#             {"name": "Pecan Pie", "description": "Southern style classic sweet pecan pie served with vanilla ice cream.", "price": "9", "is_featured": False}
#         ],
#         "cafe": [
#             {"name": "Avocado Toast", "description": "Sourdough toast topped with smashed avocado, cherry tomatoes, and feta cheese.", "price": "12", "is_featured": True},
#             {"name": "Almond Croissant", "description": "Flaky buttery croissant filled and topped with sweet almond frangipane.", "price": "6", "is_featured": True},
#             {"name": "Cappuccino", "description": "Double shot of espresso with equal parts steamed milk and foam.", "price": "5", "is_featured": False},
#             {"name": "Cheesecake", "description": "New York style rich cheesecake topped with raspberry coulis.", "price": "9", "is_featured": False}
#         ],
#         "family": [
#             {"name": "Classic Beef Burger", "description": "Flame-grilled beef patty with cheese, lettuce, tomato, pickles, and burger sauce.", "price": "12", "is_featured": True},
#             {"name": "Caesar Salad", "description": "Crispy romaine lettuce, parmesan cheese, croutons, tossed in Caesar dressing.", "price": "10", "is_featured": True},
#             {"name": "Chicken Wings", "description": "Crispy chicken wings tossed in your choice of buffalo or BBQ sauce.", "price": "11", "is_featured": False},
#             {"name": "Chocolate Fudge Cake", "description": "Warm rich chocolate cake served with vanilla bean ice cream.", "price": "8", "is_featured": False}
#         ]
#     }
    
#     return menus.get(cuisine, menus["family"])

# async def seed_demo_content(client: Client, db: AsyncSession):
#     # 1. Business hours — sensible default, editable later
#     default_hours = [
#         BusinessHours(client_id=client.id, day_of_week=d, open_time="12:00", close_time="23:00", is_closed=False)
#         for d in range(7)
#     ]
#     db.add_all(default_hours)

#     # 2. Starter menu — templated by cuisine keyword guessed from business_name
#     category = MenuCategory(client_id=client.id, name="Popular Picks", sort_order=0)
#     db.add(category)
#     await db.flush()  # get category.id

#     starter_items = get_starter_menu_for(client.business_name)
#     for item in starter_items:
#         db.add(MenuItem(client_id=client.id, category_id=category.id, **item))

#     await db.commit()


from ..models import Client, BusinessHours, MenuCategory, MenuItem
from sqlalchemy.ext.asyncio import AsyncSession
import re

def get_cuisine_type(name: str, niche: str = "") -> str:
    """
    Detect cuisine/category from business name keywords OR niche string.
    niche comes from the API payload (normalised from Agent2's plural strings).
    name-based detection is the primary signal; niche is the fallback.
    """
    name_lower = (name or "").lower()
    niche_lower = (niche or "").lower()

    # Name-based detection (most reliable)
    if any(k in name_lower for k in ["pizza", "italian", "pasta", "mario", "trattoria", "pizzeria"]):
        return "italian"
    if any(k in name_lower for k in ["sushi", "japanese", "ramen", "tokyo", "sakura", "kyoto"]):
        return "japanese"
    if any(k in name_lower for k in ["taco", "mexican", "burrito", "cantina", "mex", "el paso"]):
        return "mexican"
    if any(k in name_lower for k in ["steak", "grill", "barbecue", "bbq", "smoke", "smokehouse", "ribs"]):
        return "steakhouse"
    if any(k in name_lower for k in ["cafe", "coffee", "bakery", "bread", "sweet", "bites", "brew"]):
        return "cafe"

    # Niche-based fallback (when name doesn't give a signal)
    if any(k in niche_lower for k in ["dental", "dentist", "orthodont", "clinic", "health", "medical", "spa", "salon", "gym"]):
        return "health"

    return "family"

def get_starter_menu_for(business_name: str, niche: str = ""):
    cuisine = get_cuisine_type(business_name, niche)
    
    menus = {
        "italian": [
            {"name": "Margherita Pizza", "description": "Classic fresh mozzarella, tomato sauce, fresh basil, extra virgin olive oil.", "price": "12", "is_featured": True},
            {"name": "Fettuccine Alfredo", "description": "Rich creamy butter and parmesan sauce over tender house-made fettuccine.", "price": "16", "is_featured": True},
            {"name": "Bruschetta", "description": "Grilled bread rubbed with garlic, topped with diced tomatoes, fresh basil, olive oil.", "price": "8", "is_featured": False},
            {"name": "Tiramisu", "description": "Espresso-soaked ladyfingers layered with whipped mascarpone cheese and cocoa.", "price": "9", "is_featured": False}
        ],
        "japanese": [
            {"name": "Salmon Nigiri", "description": "Fresh slices of premium raw salmon served over seasoned sushi rice.", "price": "18", "is_featured": True},
            {"name": "Tonkotsu Ramen", "description": "Rich pork bone broth, chashu pork, soft boiled egg, scallions, bamboo shoots, seaweed.", "price": "19", "is_featured": True},
            {"name": "Vegetable Tempura", "description": "Crispy battered and deep-fried seasonal vegetables served with dipping sauce.", "price": "12", "is_featured": False},
            {"name": "Matcha Ice Cream", "description": "Creamy traditional green tea flavored dessert.", "price": "7", "is_featured": False}
        ],
        "mexican": [
            {"name": "Beef Tacos", "description": "Three corn tortillas filled with seasoned beef, cilantro, onions, and fresh lime.", "price": "11", "is_featured": True},
            {"name": "Chicken Burrito", "description": "Large flour tortilla stuffed with grilled chicken, rice, beans, cheese, and salsa.", "price": "13", "is_featured": True},
            {"name": "Guacamole & Chips", "description": "Freshly made avocado dip served with crispy house-made tortilla chips.", "price": "8", "is_featured": False},
            {"name": "Churros", "description": "Fried dough pastry dusted with cinnamon sugar, served with chocolate sauce.", "price": "7", "is_featured": False}
        ],
        "steakhouse": [
            {"name": "Ribeye Steak", "description": "12oz USDA Prime ribeye steak grilled to your liking, served with herb butter.", "price": "45", "is_featured": True},
            {"name": "Smoked Brisket", "description": "Slow-smoked beef brisket, tender and juicy, glazed with house BBQ sauce.", "price": "28", "is_featured": True},
            {"name": "Mac and Cheese", "description": "Creamy baked macaroni with a blend of cheddar, monterey jack, and breadcrumbs.", "price": "10", "is_featured": False},
            {"name": "Pecan Pie", "description": "Southern style classic sweet pecan pie served with vanilla ice cream.", "price": "9", "is_featured": False}
        ],
        "cafe": [
            {"name": "Avocado Toast", "description": "Sourdough toast topped with smashed avocado, cherry tomatoes, and feta cheese.", "price": "12", "is_featured": True},
            {"name": "Almond Croissant", "description": "Flaky buttery croissant filled and topped with sweet almond frangipane.", "price": "6", "is_featured": True},
            {"name": "Cappuccino", "description": "Double shot of espresso with equal parts steamed milk and foam.", "price": "5", "is_featured": False},
            {"name": "Cheesecake", "description": "New York style rich cheesecake topped with raspberry coulis.", "price": "9", "is_featured": False}
        ],
        # Dental, medical, salon, spa, gym — not food, so no real menu.
        # We seed "services" as menu items so the site still looks complete.
        "health": [
            {"name": "Consultation", "description": "Initial assessment and personalised treatment planning with our specialist.", "price": "0", "is_featured": True},
            {"name": "Routine Check-up", "description": "Comprehensive examination to keep you in optimal health.", "price": "99", "is_featured": True},
            {"name": "Premium Treatment", "description": "Advanced care using the latest techniques and equipment.", "price": "199", "is_featured": False},
            {"name": "Follow-up Visit", "description": "Post-treatment review to monitor your progress and adjust the plan.", "price": "49", "is_featured": False}
        ],
        "family": [
            {"name": "Classic Beef Burger", "description": "Flame-grilled beef patty with cheese, lettuce, tomato, pickles, and burger sauce.", "price": "12", "is_featured": True},
            {"name": "Caesar Salad", "description": "Crispy romaine lettuce, parmesan cheese, croutons, tossed in Caesar dressing.", "price": "10", "is_featured": True},
            {"name": "Chicken Wings", "description": "Crispy chicken wings tossed in your choice of buffalo or BBQ sauce.", "price": "11", "is_featured": False},
            {"name": "Chocolate Fudge Cake", "description": "Warm rich chocolate cake served with vanilla bean ice cream.", "price": "8", "is_featured": False}
        ]
    }
    
    return menus.get(cuisine, menus["family"])

async def seed_demo_content(client: Client, db: AsyncSession):
    # 1. Business hours — sensible default, editable later
    default_hours = [
        BusinessHours(client_id=client.id, day_of_week=d, open_time="12:00", close_time="23:00", is_closed=False)
        for d in range(7)
    ]
    db.add_all(default_hours)

    # 2. Starter menu — templated by cuisine keyword guessed from business_name
    cuisine = get_cuisine_type(client.business_name, client.niche or "")
    category_name = "Our Services" if cuisine == "health" else "Popular Picks"
    category = MenuCategory(client_id=client.id, name=category_name, sort_order=0)
    db.add(category)
    await db.flush()  # get category.id

    starter_items = get_starter_menu_for(client.business_name, client.niche or "")
    for item in starter_items:
        db.add(MenuItem(client_id=client.id, category_id=category.id, **item))

    await db.commit()