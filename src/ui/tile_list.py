class TileList:
    def __init__(self, inventory_manager, language):
        self.inventory_manager = inventory_manager
        self.language = language
        self.tiles = self.create_tiles()

    def create_tiles(self):
        tiles = []
        for item_id, item in self.inventory_manager.get_inventory_items().items():
            tiles.append({
                'id': item_id,
                'name': item['name'],
                'quantity': item['quantity']
            })
        return tiles

    def display_tiles(self):
        for tile in self.tiles:
            print(f"Item: {tile['name']} (ID: {tile['id']}) - Quantity: {tile['quantity']}")

    def update_quantity(self, item_id, change):
        if item_id in self.inventory_manager.get_inventory_items():
            self.inventory_manager.update_quantity(item_id, change)
            self.tiles = self.create_tiles()  # Refresh tiles after update
        else:
            print("Item not found in inventory.")