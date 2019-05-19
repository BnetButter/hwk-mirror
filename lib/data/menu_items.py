"""default menu"""

DEFAULT_MENU = {
    "menu": {
        "Dinners": {
            "Roast Beef": {
                "Price": 880,
                "Options": {}
            },
            "Hamburger Steak": {
                "Price": 880,
                "Options": {}
            },
            "Fried Chicken": {
                "Price": 880,
                "Options": {}
            }
        },
        "Sandwich": {
            "Hamburger": {
                "Price": 425,
                "Options": {
                    "Lettuce": 0,
                    "Tomatoes": 0,
                    "Pickles": 0,
                    "Onions": 0,
                    "Another": 0,
                    "Thing": 0
                }
            },
            "Cheeseburger": {
                "Price": 470,
                "Options": {}
            },
            "Double Hamburger": {
                "Price": 605,
                "Options": {}
            },
            "Double Cheeseburger": {
                "Price": 655,
                "Options": {}
            },
            "Grilled Ham/Beef": {
                "Price": 545,
                "Options": {}
            },
            "Cold Hamburger": {
                "Price": 470,
                "Options": {}
            },
            "Breaded Chicken": {
                "Price": 495,
                "Options": {}
            },
            "Chicken Fried Steak": {
                "Price": 525,
                "Options": {}
            },
            "Roast Beef": {
                "Price": 695,
                "Options": {}
            },
            "Daily Special": {
                "Price": 470,
                "Options": {}
            },
            "Hotdog": {
                "Price": 250,
                "Options": {}
            },
            "Grilled Cheese": {
                "Price": 305,
                "Options": {}
            }
        },
        "Snacks": {
            "Chips": {
                "Price": 60,
                "Options": {}
            },
            "Candy Bar": {
                "Price": 145,
                "Options": {}
            },
            "Peanuts": {
                "Price": 55,
                "Options": {}
            },
            "Trail Mix": {
                "Price": 100,
                "Options": {}
            },
            "Nutter Butters": {
                "Price": 100,
                "Options": {}
            }
        },
        "Sides": {
            "Chef Salad": {
                "Price": 635,
                "Options": {}
            },
            "Dinner Salad": {
                "Price": 305,
                "Options": {}
            },
            "French Fries": {
                "Price": 220,
                "Options": {}
            },
            "Tater Tots": {
                "Price": 275,
                "Options": {}
            },
            "Onion Rings": {
                "Price": 305,
                "Options": {}
            },
            "Seasoned Fries": {
                "Price": 275,
                "Options": {}
            }
        },
        "Dessert": {
            "Pie": {
                "Price": 320,
                "Options": {}
            },
            "Brownie": {
                "Price": 220,
                "Options": {}
            },
            "Cake": {
                "Price": 220,
                "Options": {}
            }
        },
        "Drinks": {
            "Bottled Soda": {
                "Price": 220,
                "Options": {}
            },
            "Tea": {
                "Price": 220,
                "Options": {}
            },
            "Bottled Water": {
                "Price": 100,
                "Options": {}
            },
            "Water cup": {
                "Price": 50,
                "Options": {}
            },
            "Coffee": {
                "Price": 100,
                "Options": {
                    "Sizes": {
                        "Small": 0,
                        "Medium": 25,
                        "Large": 100
                    }
                }
            },
            "Hot Chocolate": {
                "Price": 200,
                "Options": {}
            }
        }
    },
    "config": {
        "Tax": 8.55,
        "No Addons": [
            "Sides",
            "Drinks",
            "Snacks"
        ],
        "Sides Included": [],
        "Drinks Included": [],
        "Two Sides": [
            "Dinners"
        ],
        "Register":["Drinks", "Snacks"],
        "Payment Types":[
            "Cash",
            "Check",
            "Invoice",
        ]
    }
}