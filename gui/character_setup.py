# ... existing code ...

# Lines 130-136 modified to use grid()
refresh_button = Button(self, text="Refresh", command=self.refresh)
refresh_button.grid(row=0, column=0)  # Example grid placement

test_button = Button(self, text="Test", command=self.test)
test_button.grid(row=0, column=1)  # Example grid placement

# Update toggle_api_fields method
def toggle_api_fields(self):
    # Example code for handling grid positioning
    if self.api_enabled.get():
        self.api_key_label.grid(row=1, column=0)  # Example grid placement
        self.api_key_entry.grid(row=1, column=1)  # Example grid placement
    else:
        self.api_key_label.grid_forget()
        self.api_key_entry.grid_forget()