import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkthemes import ThemedTk
import json
from datetime import datetime, timedelta
import threading
from tkinter import messagebox, colorchooser, filedialog
import os
import sys
import pygame  # For sound
from PIL import Image, ImageTk
import webbrowser
import calendar
from tkcalendar import Calendar
import pyperclip
from plyer import notification  # Add this import at the top
import urllib.parse

class CustomStyle:
    # Colors
    PRIMARY_COLOR = "#2196F3"
    SECONDARY_COLOR = "#FFC107"
    BACKGROUND_COLOR = "#FFFFFF"
    TEXT_COLOR = "#212121"
    ACCENT_COLOR = "#FF4081"
    SUCCESS_COLOR = "#4CAF50"
    WARNING_COLOR = "#FF9800"
    ERROR_COLOR = "#F44336"
    
    # Fonts
    HEADER_FONT = ("Helvetica", 16, "bold")
    NORMAL_FONT = ("Helvetica", 12)
    SMALL_FONT = ("Helvetica", 10)
    
    # Padding and margins
    PADDING = 10
    MARGIN = 5

    # Button Colors
    BUTTON_COLORS = {
        'save': {"bg": "#4CAF50", "fg": "white", "hover_bg": "#45a049"},      # Green
        'delete': {"bg": "#f44336", "fg": "white", "hover_bg": "#da190b"},    # Red
        'share': {"bg": "#2196F3", "fg": "white", "hover_bg": "#1976D2"},     # Blue
        'complete': {"bg": "#4CAF50", "fg": "white", "hover_bg": "#45a049"},  # Green
        'snooze': {"bg": "#FF9800", "fg": "white", "hover_bg": "#F57C00"},    # Orange
        'dismiss': {"bg": "#757575", "fg": "white", "hover_bg": "#616161"},   # Gray
        'calendar': {"bg": "#9C27B0", "fg": "white", "hover_bg": "#7B1FA2"},  # Purple
        'quick_add': {"bg": "#00BCD4", "fg": "white", "hover_bg": "#0097A7"}, # Cyan
    }

    @classmethod
    def create_styled_button(cls, parent, text, command, style='default'):
        """Create a styled button with hover effect"""
        button_frame = ttk.Frame(parent)
        
        # Create a custom styled button
        button = tk.Button(
            button_frame,
            text=text,
            command=command,
            cursor="hand2",
            relief="flat",
            overrelief="flat",
            bd=0,
            padx=10,
            pady=5,
            font=cls.NORMAL_FONT
        )
        
        # Apply color scheme based on style
        colors = cls.BUTTON_COLORS.get(style.lower(), {
            "bg": "#e0e0e0",
            "fg": "black",
            "hover_bg": "#d5d5d5"
        })
        
        button.configure(
            bg=colors["bg"],
            fg=colors["fg"],
            activebackground=colors["hover_bg"],
            activeforeground=colors["fg"]
        )
        
        # Hover effects
        def on_enter(e):
            button['background'] = colors["hover_bg"]
            
        def on_leave(e):
            button['background'] = colors["bg"]
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        button.pack(expand=True, fill="both")
        return button_frame

class TaskReminder:
    def __init__(self, root):
        self.root = root
        self.app_name = "Task Reminder"  # Add this line for consistent naming
        self.root.title(self.app_name)
        self.root.geometry("1200x800")
        
        # Define icon path
        self.icon_path = "C:/Users/SEC/Downloads/pw/task_complete_icon-removebg-preview.ico"
        
        # Set main window icon
        self.set_window_icon(self.root)
        
        self.root.set_theme("arc")
        
        # Initialize pygame for sounds
        pygame.mixer.init()
        
        # Initialize variables
        self.tasks = []
        self.categories = ["Work", "Personal", "Shopping", "Health", "Other"]
        self.priorities = ["Low", "Normal", "Medium", "High", "Urgent"]
        self.current_theme = "light"
        self.snooze_times = [5, 10, 15, 30, 60]  # minutes
        self.active_reminders = {}
        self.next_task_id = 1  # Add counter for task IDs
        self.notification_enabled = True  # Add this line
        self.selected_date = datetime.now().strftime("%Y-%m-%d")  # Add default selected date
        
        # Add priority colors
        self.priority_colors = {
            "Urgent": "#FF0000",  # Red
            "High": "#FF6B6B",    # Light Red
            "Medium": "#FFA500",   # Orange
            "Normal": "#808080",   # Gray
            "Low": "#4CAF50"      # Green
        }
        
        # Load settings
        self.load_settings()
        
        # Create main container first
        self.create_main_container()
        self.create_header()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_split_view()
        self.create_status_bar()
        
        # Now load tasks after UI elements are created
        self.load_tasks()
        
        # Start background processes
        self.check_reminders()
        self.auto_save_timer()

        # Add style configuration
        self.style = ttk.Style()
        self.style = ttk.Style()
        self.configure_styles()

        # Add system tray icon
        self.create_system_tray()
        
        # Check if started from startup
        if '--minimized' in sys.argv:
            self.root.iconify()

    def set_window_icon(self, window):
        """Set icon for any window"""
        try:
            window.iconbitmap(self.icon_path)
        except tk.TkError:
            print(f"Warning: Could not load icon file: {self.icon_path}")

    def configure_styles(self):
        """Configure custom styles for the application"""
        self.style.configure(
            "Action.TButton",
            padding=6,
            relief="flat",
            background=CustomStyle.PRIMARY_COLOR
        )

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Tasks", command=self.import_tasks)
        file_menu.add_command(label="Export Tasks", command=self.export_tasks)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Preferences", command=self.show_preferences)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        view_menu.add_command(label="Show Calendar", command=self.show_calendar)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Statistics", command=self.show_statistics)
        tools_menu.add_command(label="Backup Data", command=self.backup_data)

    def create_toolbar(self):
        toolbar = ttk.Frame(self.main_container)
        toolbar.pack(fill=tk.X, pady=5)
        
        # Quick add task button with custom style
        quick_add_btn = CustomStyle.create_styled_button(
            toolbar, "Quick Add", self.quick_add_task, "quick_add"
        )
        quick_add_btn.pack(side=tk.LEFT, padx=2)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(toolbar, text="Filters")
        filter_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Category filter
        self.category_var = tk.StringVar(value="All")
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT, padx=2)
        category_filter = ttk.Combobox(filter_frame, textvariable=self.category_var, 
                                     values=["All"] + self.categories, width=10)
        category_filter.pack(side=tk.LEFT, padx=2)
        
        # Priority filter
        self.priority_var = tk.StringVar(value="All")
        ttk.Label(filter_frame, text="Priority:").pack(side=tk.LEFT, padx=2)
        priority_filter = ttk.Combobox(filter_frame, textvariable=self.priority_var, 
                                     values=["All"] + self.priorities, width=10)
        priority_filter.pack(side=tk.LEFT, padx=2)
        
        # Status filter
        self.status_var = tk.StringVar(value="All")
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=2)
        status_filter = ttk.Combobox(filter_frame, textvariable=self.status_var,
                                   values=["All", "Pending", "Completed"], width=10)
        status_filter.pack(side=tk.LEFT, padx=2)
        
        # Due date filter
        self.due_date_var = tk.StringVar(value="All")
        ttk.Label(filter_frame, text="Due:").pack(side=tk.LEFT, padx=2)
        due_filter = ttk.Combobox(filter_frame, textvariable=self.due_date_var,
                                values=["All", "Today", "This Week", "This Month"], width=10)
        due_filter.pack(side=tk.LEFT, padx=2)
        
        # Button group (Apply Filters, Clear, New Task)
        button_group = ttk.Frame(filter_frame)
        button_group.pack(side=tk.LEFT, padx=2)
        
        # Apply filter button
        filter_btn = CustomStyle.create_styled_button(
            button_group, "Apply Filters", self.apply_filters, "share"
        )
        filter_btn.pack(side=tk.LEFT, padx=2)
        
        # Clear filters button
        clear_btn = CustomStyle.create_styled_button(
            button_group, "Clear", self.clear_filters, "dismiss"
        )
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # New Task button (moved from details panel)
        new_task_btn = CustomStyle.create_styled_button(
            button_group, "New Task", self.clear_details_panel, "quick_add"
        )
        new_task_btn.pack(side=tk.LEFT, padx=2)
        
        # Search box remains at the right
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search)
        ttk.Entry(toolbar, textvariable=self.search_var, width=20).pack(side=tk.RIGHT, padx=2)
        ttk.Label(toolbar, text="Search:").pack(side=tk.RIGHT, padx=2)

    def apply_filters(self):
        """Apply all selected filters"""
        self.refresh_task_list()

    def clear_filters(self):
        """Reset all filters to default values"""
        self.category_var.set("All")
        self.priority_var.set("All")
        self.status_var.set("All")
        self.due_date_var.set("All")
        self.search_var.set("")
        self.refresh_task_list()

    def create_split_view(self):
        # Create notebook for multiple views
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Today Tasks view (new)
        self.today_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.today_frame, text="Today Tasks")
        self.create_today_tasks_view()
        
        # Tasks view
        self.tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_frame, text="Tasks")
        
        # Create horizontal paned window
        self.paned_window = ttk.PanedWindow(self.tasks_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left frame (Task list)
        self.create_task_list_frame()
        
        # Right frame (Details)
        self.create_details_frame()
        
        # Calendar view
        self.calendar_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.calendar_frame, text="Calendar")
        self.create_calendar_view()
        
        # Statistics view
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self.create_statistics_view()

    def create_today_tasks_view(self):
        """Create the today tasks view"""
        # Container
        container = ttk.Frame(self.today_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header
        header = ttk.Frame(container)
        header.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            header, 
            text="Tasks for Today", 
            font=CustomStyle.HEADER_FONT
        ).pack(side=tk.LEFT)

        # Tasks list
        columns = ("Task", "Time", "Category", "Priority", "Status")
        self.today_tree = ttk.Treeview(container, columns=columns, show="headings")
        
        # Configure columns
        self.today_tree.heading("Task", text="Task")
        self.today_tree.heading("Time", text="Time")
        self.today_tree.heading("Category", text="Category")
        self.today_tree.heading("Priority", text="Priority")
        self.today_tree.heading("Status", text="Status")
        
        self.today_tree.column("Task", width=200)
        self.today_tree.column("Time", width=100)
        self.today_tree.column("Category", width=100)
        self.today_tree.column("Priority", width=100)
        self.today_tree.column("Status", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.today_tree.yview)
        self.today_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.today_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # No tasks label
        self.no_tasks_label = ttk.Label(
            container,
            text="No tasks for today\nClick 'Add New Task' to create one",
            font=CustomStyle.NORMAL_FONT,
            justify=tk.CENTER
        )
        
        # Bindings
        self.today_tree.bind('<<TreeviewSelect>>', self.on_today_task_select)
        self.today_tree.bind('<Double-1>', self.edit_task)
        
        # Initial update
        self.update_today_tasks()

    def update_today_tasks(self):
        """Update the today tasks list using the main filtering system"""
        print("\nDEBUG: Starting update_today_tasks")
        
        # Clear current items
        for item in self.today_tree.get_children():
            self.today_tree.delete(item)
        
        # Store current filter settings
        old_category = self.category_var.get()
        old_priority = self.priority_var.get()
        old_status = self.status_var.get()
        old_due = self.due_date_var.get()
        
        print(f"DEBUG: Old filter settings: Category={old_category}, Priority={old_priority}, Status={old_status}, Due={old_due}")
        
        try:
            # Set filters for today's pending tasks
            self.category_var.set("All")
            self.priority_var.set("All")
            self.status_var.set("Pending")
            self.due_date_var.set("Today")
            
            print("DEBUG: Applied today's filters")
            
            # Get filtered tasks
            today_tasks = self.filter_tasks()
            print(f"DEBUG: Found {len(today_tasks)} tasks for today")
            
            if not today_tasks:
                print("DEBUG: No tasks found for today")
                self.no_tasks_label.configure(
                    text="No pending tasks for today\nClick 'New Task' at the top to create one"
                )
                self.no_tasks_label.pack(expand=True)
            else:
                self.no_tasks_label.pack_forget()
                
                # Fix the priority sorting order
                priority_order = {"Low": 0, "Normal": 1, "Medium": 2, "High": 3, "Urgent": 4}
                
                # Update sort key to use priority_order
                today_tasks.sort(key=lambda x: (
                    datetime.strptime(x['due_date'], "%Y-%m-%d %H:%M"),
                    priority_order.get(x.get('priority', 'Normal'), 0)
                ))
                
                # Add tasks to the tree view
                for task in today_tasks:
                    print(f"DEBUG: Adding task to today view: {task['name']} - {task['due_date']}")
                    task_datetime = datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M")
                    task_time = task_datetime.strftime("%H:%M")
                    
                    # Add status indicator emoji
                    display_name = task['name']
                    if datetime.now() > task_datetime:
                        display_name = "⚠️ " + display_name  # Overdue
                    elif task.get('reminder_enabled'):
                        display_name = "⏰ " + display_name  # Has reminder
                    
                    item_id = self.today_tree.insert(
                        "", "end",
                        values=(
                            display_name,
                            task_time,
                            task.get('category', 'Other'),
                            task.get('priority', 'Normal'),
                            task.get('status', 'Pending')
                        ),
                        tags=(task.get('priority', 'Normal'),)
                    )
                    
                    # Apply priority color
                    if task.get('priority') in self.priority_colors:
                        self.today_tree.tag_configure(
                            task.get('priority'),
                            foreground=self.priority_colors[task.get('priority')]
                        )
                    
                    # Highlight overdue tasks
                    if datetime.now() > task_datetime:
                        self.today_tree.tag_configure(
                            f"overdue_{item_id}",
                            background="#FFE6E6"
                        )
                        current_tags = list(self.today_tree.item(item_id, "tags"))
                        current_tags.append(f"overdue_{item_id}")
                        self.today_tree.item(item_id, tags=current_tags)

        except Exception as e:
            print(f"DEBUG: Error in update_today_tasks: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Restore original filter settings
            print("DEBUG: Restoring original filter settings")
            self.category_var.set(old_category)
            self.priority_var.set(old_priority)
            self.status_var.set(old_status)
            self.due_date_var.set(old_due)
        
        # Update statistics
        self.update_statistics()

    def create_task_list_frame(self):
        left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=1)
        
        left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=1)
        
        # Task list
        columns = ("Task", "Category", "Priority", "Due Date", "Status")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_tasks(c))
            self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bindings
        self.tree.bind('<<TreeviewSelect>>', self.on_task_select)
        self.tree.bind('<Double-1>', self.edit_task)
        self.tree.bind('<Delete>', self.delete_task)

    def create_details_frame(self):
        right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(right_frame, weight=1)
        
        # Task details
        details_frame = ttk.LabelFrame(right_frame, text="Task Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Details content
        self.details_name = ttk.Entry(details_frame)
        self.details_name.pack(fill=tk.X, padx=5, pady=5)
        
        # Category and Priority
        cp_frame = ttk.Frame(details_frame)
        cp_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.details_category = ttk.Combobox(cp_frame, values=self.categories)
        self.details_category.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.details_priority = ttk.Combobox(cp_frame, values=self.priorities)
        self.details_priority.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Due date with calendar picker
        date_frame = ttk.Frame(details_frame)
        date_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.details_date = ttk.Entry(date_frame)
        self.details_date.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        reminder_frame = ttk.LabelFrame(details_frame, text="Reminders")
        reminder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        reminder_frame = ttk.LabelFrame(details_frame, text="Reminders")
        reminder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.reminder_enabled = tk.BooleanVar()
        ttk.Checkbutton(reminder_frame, text="Enable Reminders", variable=self.reminder_enabled).pack()
        
        # Add reminder type frame
        reminder_type_frame = ttk.Frame(reminder_frame)
        reminder_type_frame.pack(fill=tk.X, pady=5)
        
        # Standard reminder options
        self.reminder_time = ttk.Combobox(reminder_type_frame, values=["5 min", "15 min", "30 min", "1 hour", "1 day"])
        self.reminder_time.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Custom reminder button
        ttk.Button(reminder_type_frame, text="Custom Reminder", command=self.show_custom_reminder_dialog).pack(side=tk.LEFT, padx=2)
        
        # Notes
        notes_frame = ttk.LabelFrame(details_frame, text="Notes")
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.notes_text = scrolledtext.ScrolledText(notes_frame, height=10)
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add New Task button
        new_task_btn = CustomStyle.create_styled_button(
            button_frame, "New Task", self.clear_details_panel, "quick_add"
        )
        new_task_btn.pack(side=tk.LEFT, padx=2)
        
        # Save button
        save_btn = CustomStyle.create_styled_button(
            button_frame, "Save", self.save_task_details, "save"
        )
        save_btn.pack(side=tk.LEFT, padx=2)
        
        # Delete button
        delete_btn = CustomStyle.create_styled_button(
            button_frame, "Delete", self.delete_task, "delete"
        )
        delete_btn.pack(side=tk.LEFT, padx=2)
        
        # Share button
        share_btn = CustomStyle.create_styled_button(
            button_frame, "Share", self.share_task, "share"
        )
        share_btn.pack(side=tk.LEFT, padx=2)

        # Add reminder management section
        reminder_list_frame = ttk.LabelFrame(details_frame, text="Active Reminders")
        reminder_list_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create reminder list
        self.reminder_list = ttk.Treeview(reminder_list_frame, 
                                        columns=("Date", "Time"),
                                        show="headings",
                                        height=3)
        self.reminder_list.heading("Date", text="Date")
        self.reminder_list.heading("Time", text="Time")
        self.reminder_list.pack(fill=tk.X, pady=2)
        
        # Delete reminder button
        delete_reminder_btn = CustomStyle.create_styled_button(
            reminder_list_frame, "Delete Selected Reminder", 
            self.delete_reminder, "delete"
        )
        delete_reminder_btn.pack(fill=tk.X, pady=2)

    def create_calendar_view(self):
        # Create container frame
        calendar_container = ttk.Frame(self.calendar_frame)
        calendar_container.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Calendar
        calendar_left = ttk.Frame(calendar_container)
        calendar_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Calendar widget
        self.cal = Calendar(calendar_left, selectmode='day',
                          year=datetime.now().year,
                          month=datetime.now().month,
                          day=datetime.now().day)
        self.cal.pack(pady=10)
        
        # Right side: Task list
        calendar_right = ttk.Frame(calendar_container)
        calendar_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Date label
        self.calendar_date_label = ttk.Label(calendar_right, 
                                           text="Selected Date Tasks", 
                                           font=CustomStyle.HEADER_FONT)
        self.calendar_date_label.pack(pady=5)
        
        # Task list
        columns = ("Time", "Task", "Priority", "Status")
        self.cal_task_list = ttk.Treeview(calendar_right, 
                                         columns=columns, 
                                         show="headings",
                                         height=15)
        
        # Configure columns
        self.cal_task_list.heading("Time", text="Time")
        self.cal_task_list.heading("Task", text="Task")
        self.cal_task_list.heading("Priority", text="Priority")
        self.cal_task_list.heading("Status", text="Status")
        
        self.cal_task_list.column("Time", width=100)
        self.cal_task_list.column("Task", width=200)
        self.cal_task_list.column("Priority", width=100)
        self.cal_task_list.column("Status", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(calendar_right, orient=tk.VERTICAL, 
                                command=self.cal_task_list.yview)
        self.cal_task_list.configure(yscrollcommand=scrollbar.set)
        
        # Pack list and scrollbar
        self.cal_task_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.cal.bind('<<CalendarSelected>>', self.update_calendar_tasks)
        self.cal_task_list.bind('<Double-1>', self.edit_calendar_task)
        
        # Update tasks for current date
        self.update_calendar_tasks()

    def create_statistics_view(self):
        """Create an enhanced statistics view using grid layout"""
        stats_container = ttk.Frame(self.stats_frame)
        stats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure grid weights
        stats_container.grid_columnconfigure(0, weight=1)
        stats_container.grid_columnconfigure(1, weight=1)
        
        # Header
        ttk.Label(
            stats_container, 
            text="Task Statistics Dashboard", 
            font=CustomStyle.HEADER_FONT
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Overview Section
        overview_frame = ttk.LabelFrame(stats_container, text="Overview")
        overview_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Category Section
        category_frame = ttk.LabelFrame(stats_container, text="Categories")
        category_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Priority Section
        priority_frame = ttk.LabelFrame(stats_container, text="Priorities")
        priority_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        
        # Status Section
        status_frame = ttk.LabelFrame(stats_container, text="Status")
        status_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        
        # Store labels as instance variables for updating
        self.stats_labels = {
            'overview': {},
            'category': {},
            'priority': {},
            'status': {}
        }
        
        # Create initial labels
        self.create_stats_section(overview_frame, 'overview')
        self.create_stats_section(category_frame, 'category')
        self.create_stats_section(priority_frame, 'priority')
        self.create_stats_section(status_frame, 'status')
        
        # Update statistics
        self.update_statistics()

    def create_stats_section(self, parent, section):
        """Create labels for a statistics section"""
        if section == 'overview':
            headers = ['Total Tasks:', 'Completed Tasks:', 'Pending Tasks:', 'Completion Rate:']
            for i, header in enumerate(headers):
                ttk.Label(parent, text=header, font=CustomStyle.NORMAL_FONT).grid(
                    row=i, column=0, sticky="w", padx=10, pady=5
                )
                value_label = ttk.Label(parent, text="0", font=CustomStyle.NORMAL_FONT)
                value_label.grid(row=i, column=1, sticky="e", padx=10, pady=5)
                self.stats_labels['overview'][header] = value_label
        else:
            # Create a treeview for categories, priorities, and status
            tree = ttk.Treeview(parent, columns=('Item', 'Count', 'Percentage'), 
                               show='headings', height=5)
            tree.heading('Item', text='Item')
            tree.heading('Count', text='Count')
            tree.heading('Percentage', text='Percentage')
            
            tree.column('Item', width=100)
            tree.column('Count', width=70)
            tree.column('Percentage', width=90)
            
            tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
            scrollbar.grid(row=0, column=1, sticky="ns")
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Configure grid weights
            parent.grid_columnconfigure(0, weight=1)
            parent.grid_rowconfigure(0, weight=1)
            
            self.stats_labels[section] = tree

    def update_statistics(self):
        """Update statistics display with enhanced visualization"""
        if not hasattr(self, 'stats_labels'):
            return
            
        stats = self.calculate_statistics()
        
        # Update Overview section
        overview_data = {
            'Total Tasks:': str(stats['total']),
            'Completed Tasks:': str(stats['completed']),
            'Pending Tasks:': str(stats['pending']),
            'Completion Rate:': f"{stats['completion_rate']:.1f}%"
        }
        
        for label, value in overview_data.items():
            if label in self.stats_labels['overview']:
                self.stats_labels['overview'][label].config(text=value)
        
        # Update Category section
        category_tree = self.stats_labels['category']
        category_tree.delete(*category_tree.get_children())
        total = stats['total'] or 1  # Avoid division by zero
        for cat, count in stats['by_category'].items():
            percentage = (count / total) * 100
            category_tree.insert('', 'end', values=(cat, count, f"{percentage:.1f}%"))
        
        # Update Priority section
        priority_tree = self.stats_labels['priority']
        priority_tree.delete(*priority_tree.get_children())
        for pri, count in stats['by_priority'].items():
            percentage = (count / total) * 100
            priority_tree.insert('', 'end', values=(pri, count, f"{percentage:.1f}%"))
        
        # Update Status section
        status_tree = self.stats_labels['status']
        status_tree.delete(*status_tree.get_children())
        status_data = {
            'Completed': stats['completed'],
            'Pending': stats['pending']
        }
        for status, count in status_data.items():
            percentage = (count / total) * 100
            status_tree.insert('', 'end', values=(status, count, f"{percentage:.1f}%"))

    def show_snooze_dialog(self, task_id):
        dialog = tk.Toplevel(self.root)
        dialog.title("Snooze Reminder")
        dialog.geometry("300x200")
        self.set_window_icon(dialog)  # Add icon
        
        ttk.Label(dialog, text="Snooze for:").pack(pady=10)
        
        for time in self.snooze_times:
            ttk.Button(
                dialog,
                text=f"{time} minutes",
                command=lambda t=time: self.snooze_reminder(task_id, t, dialog)
            ).pack(pady=5)
        
        ttk.Button(dialog, text="Dismiss", command=dialog.destroy).pack(pady=10)

    def snooze_reminder(self, task_id, minutes, dialog):
        # Update next reminder time
        for task in self.tasks:
            if task.get('id') == task_id:
                task['next_reminder'] = (datetime.now() + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M")
                break
        
        self.save_tasks()
        dialog.destroy()

    def play_reminder_sound(self):
        """Play reminder sound if available"""
        try:
            # Try system beep first as it's more reliable
            import winsound
            winsound.Beep(1000, 500)  # frequency=1000Hz, duration=500ms
        except Exception as e:
            try:
                # Fallback to pygame if system beep fails
                sound_file = 'reminder.wav'
                if os.path.exists(sound_file):
                    pygame.mixer.music.load(sound_file)
                    pygame.mixer.music.play()
            except Exception as e:
                print(f"Error playing sound: {e}")

    def import_tasks(self):
        filename = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    imported_tasks = json.load(f)
                self.tasks.extend(imported_tasks)
                self.save_tasks()
                self.refresh_task_list()
                messagebox.showinfo("Success", "Tasks imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error importing tasks: {str(e)}")

    def export_tasks(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.tasks, f, indent=4)
                messagebox.showinfo("Success", "Tasks exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting tasks: {str(e)}")

    def show_preferences(self):
        pref_window = tk.Toplevel(self.root)
        pref_window.title("Preferences")
        pref_window.geometry("400x300")
        self.set_window_icon(pref_window)  # Add icon
        
        # Sound preferences
        sound_frame = ttk.LabelFrame(pref_window, text="Sound Settings")
        sound_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.sound_enabled = tk.BooleanVar(value=self.settings.get('sound_enabled', True))
        ttk.Checkbutton(sound_frame, text="Enable Sounds", variable=self.sound_enabled).pack(padx=5, pady=5)
        
        # Add notification preferences
        notification_frame = ttk.LabelFrame(pref_window, text="Notification Settings")
        notification_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.notification_enabled = tk.BooleanVar(value=self.settings.get('notification_enabled', True))
        ttk.Checkbutton(notification_frame, text="Enable System Notifications", 
                       variable=self.notification_enabled).pack(padx=5, pady=5)
        
        # Default reminder times
        reminder_frame = ttk.LabelFrame(pref_window, text="Default Reminder Settings")
        reminder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.default_reminder_time = tk.StringVar(value=self.settings.get('default_reminder', '15'))
        ttk.Label(reminder_frame, text="Default reminder time (minutes):").pack()
        ttk.Entry(reminder_frame, textvariable=self.default_reminder_time).pack(padx=5, pady=5)
        
        # Auto-save interval
        autosave_frame = ttk.LabelFrame(pref_window, text="Auto-Save Settings")
        autosave_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.autosave_interval = tk.StringVar(value=self.settings.get('autosave_interval', '5'))
        ttk.Label(autosave_frame, text="Auto-save interval (minutes):").pack()
        ttk.Entry(autosave_frame, textvariable=self.autosave_interval).pack(padx=5, pady=5)
        
        # Save button
        ttk.Button(pref_window, text="Save Preferences", command=lambda: self.save_preferences(pref_window)).pack(pady=10)

    def save_preferences(self, window):
        self.settings['sound_enabled'] = self.sound_enabled.get()
        self.settings['notification_enabled'] = self.notification_enabled.get()
        self.settings['default_reminder'] = self.default_reminder_time.get()
        self.settings['autosave_interval'] = self.autosave_interval.get()
        
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)
        
        window.destroy()
        self.status_bar.config(text="Preferences saved successfully")

    def toggle_theme(self):
        if self.current_theme == "light":
            self.root.set_theme("equilux")  # Dark theme
            self.current_theme = "dark"
        else:
            self.root.set_theme("arc")  # Light theme
            self.current_theme = "light"
        
        self.settings['theme'] = self.current_theme
        self.save_settings()

    def show_calendar(self):
        cal_window = tk.Toplevel(self.root)
        cal_window.title("Calendar View")
        cal_window.geometry("800x600")
        self.set_window_icon(cal_window)  # Add icon
        
        # Create calendar widget
        cal = Calendar(cal_window, selectmode='day',
                      year=datetime.now().year,
                      month=datetime.now().month,
                      day=datetime.now().day)
        cal.pack(pady=10)
        
        # Tasks for selected date
        task_frame = ttk.Frame(cal_window)
        task_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        task_list = ttk.Treeview(task_frame, columns=("Task", "Time", "Priority"),
                                show="headings")
        task_list.pack(fill=tk.BOTH, expand=True)
        
        def update_tasks(event):
            selected_date = cal.get_date()
            # Clear current items
            for item in task_list.get_children():
                task_list.delete(item)
            # Add tasks for selected date
            for task in self.tasks:
                if task['due_date'].startswith(selected_date):
                    task_list.insert("", "end", values=(task['name'],
                                                      task['due_date'],
                                                      task.get('priority', 'Normal')))
        
        cal.bind('<<CalendarSelected>>', update_tasks)

    def show_statistics(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Task Statistics")
        stats_window.geometry("600x400")
        self.set_window_icon(stats_window)  # Add icon
        
        # Calculate statistics
        stats = self.calculate_statistics()
        
        # Create labels with statistics
        ttk.Label(stats_window, text="Task Statistics", font=CustomStyle.HEADER_FONT).pack(pady=10)
        
        stats_text = f"""
        Task Overview:
        -------------
        Total Tasks: {stats['total']}
        Completed Tasks: {stats['completed']}
        Pending Tasks: {stats['pending']}
        Completion Rate: {stats['completion_rate']:.1f}%
        
        Tasks by Category:
        ----------------
        {chr(10).join(f'{cat}: {count}' for cat, count in stats['by_category'].items())}
        
        Tasks by Priority:
        ----------------
        {chr(10).join(f'{pri}: {count}' for pri, count in stats['by_priority'].items())}
        """
        
        ttk.Label(stats_window, text=stats_text, justify=tk.LEFT).pack(pady=10, padx=10)

    def calculate_statistics(self):
        """Calculate various statistics about tasks"""
        stats = {}
        
        # Basic counts
        stats['total'] = len(self.tasks)
        stats['completed'] = len([t for t in self.tasks if t.get('status') == 'Completed'])
        stats['pending'] = stats['total'] - stats['completed']
        stats['completion_rate'] = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        # Category statistics
        stats['by_category'] = {}
        for task in self.tasks:
            category = task.get('category', 'Other')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        # Priority statistics
        stats['by_priority'] = {}
        for task in self.tasks:
            priority = task.get('priority', 'Normal')
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        return stats

    def backup_data(self):
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"tasks_backup_{timestamp}.json")
        
        try:
            with open(backup_file, 'w') as f:
                json.dump(self.tasks, f, indent=4)
            self.status_bar.config(text=f"Backup created: {backup_file}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Error creating backup: {str(e)}")

    def quick_add_task(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Quick Add Task")
        dialog.geometry("400x200")
        self.set_window_icon(dialog)  # Add icon
        
        ttk.Label(dialog, text="Task Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Due Date (YYYY-MM-DD HH:MM):").pack(pady=5)
        date_entry = ttk.Entry(dialog, width=40)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        date_entry.pack(pady=5)
        
        def add():
            name = name_entry.get()
            date = date_entry.get()
            
            if name and date:
                task = {
                    "id": self.next_task_id,
                    "name": name,
                    "due_date": date,
                    "status": "Pending",
                    "category": "Other",
                    "priority": "Normal",
                    "notes": "",  # Initialize notes as empty string
                    "reminder_enabled": False,  # Add default reminder setting
                    "reminder_time": "15 min"  # Add default reminder time
                }
                
                self.next_task_id += 1
                self.tasks.append(task)
                self.save_tasks()
                self.refresh_task_list()
                dialog.destroy()
            else:
                messagebox.showwarning("Invalid Input", "Please fill in all fields")
        
        ttk.Button(dialog, text="Add Task", command=add).pack(pady=10)

    def share_task(self):
        """Enhanced share functionality with multiple options"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        task = self.get_task_by_id(selected_items[0])
        if task:
            share_window = tk.Toplevel(self.root)
            share_window.title("Share Task")
            share_window.geometry("300x400")
            self.set_window_icon(share_window)  # Add icon
            
            # Create share text
            share_text = f"""
Task: {task['name']}
Due Date: {task['due_date']}
Status: {task['status']}
Category: {task.get('category', 'Other')}
Priority: {task.get('priority', 'Normal')}
Notes: {task.get('notes', '')}
"""
            # Show preview
            ttk.Label(share_window, text="Share Options", font=CustomStyle.HEADER_FONT).pack(pady=10)
            preview = scrolledtext.ScrolledText(share_window, height=6)
            preview.insert('1.0', share_text)
            preview.pack(padx=10, pady=5, fill=tk.X)
            
            # Share buttons frame
            button_frame = ttk.Frame(share_window)
            button_frame.pack(pady=10, fill=tk.X, padx=10)
            
            def copy_to_clipboard():
                pyperclip.copy(share_text)
                self.status_bar.config(text="Task details copied to clipboard")
                
            def share_via_email():
                subject = urllib.parse.quote(f"Task: {task['name']}")
                body = urllib.parse.quote(share_text)
                webbrowser.open(f'mailto:?subject={subject}&body={body}')
                
            def share_via_whatsapp():
                text = urllib.parse.quote(share_text)
                webbrowser.open(f'https://wa.me/?text={text}')
            
            def share_via_teams():
                text = urllib.parse.quote(share_text)
                webbrowser.open(f'https://teams.microsoft.com/share?text={text}')
            
            # Share buttons with icons and colors
            CustomStyle.create_styled_button(
                button_frame, "📋 Copy to Clipboard", 
                copy_to_clipboard, "share"
            ).pack(fill=tk.X, pady=2)
            
            CustomStyle.create_styled_button(
                button_frame, "📧 Email", 
                share_via_email, "share"
            ).pack(fill=tk.X, pady=2)
            
            CustomStyle.create_styled_button(
                button_frame, "📱 WhatsApp", 
                share_via_whatsapp, "share"
            ).pack(fill=tk.X, pady=2)
            
            CustomStyle.create_styled_button(
                button_frame, "👥 Microsoft Teams", 
                share_via_teams, "share"
            ).pack(fill=tk.X, pady=2)
            
            # Close button
            CustomStyle.create_styled_button(
                share_window, "Close", 
                share_window.destroy, "dismiss"
            ).pack(pady=10)

            # Make window modal
            share_window.transient(self.root)
            share_window.grab_set()
            self.root.wait_window(share_window)

    def auto_save_timer(self):
        self.save_tasks()
        interval = int(self.settings.get('autosave_interval', 5)) * 60 * 1000  # Convert to milliseconds
        self.root.after(interval, self.auto_save_timer)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {
                'sound_enabled': True,
                'notification_enabled': True,  # Add this line
                'default_reminder': '15',
                'autosave_interval': '5',
                'theme': 'light'
            }
            self.save_settings()

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)

    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            with open('tasks.json', 'r') as f:
                self.tasks = json.load(f)
                print(f"\nDEBUG: Loaded {len(self.tasks)} tasks from file")
                
                # Ensure all tasks have IDs
                max_id = 0
                for task in self.tasks:
                    if 'id' not in task:
                        max_id += 1
                        task['id'] = max_id
                    else:
                        max_id = max(max_id, task['id'])
                    print(f"DEBUG: Task loaded - Name: {task['name']}, Due: {task['due_date']}, Status: {task.get('status')}")
                self.next_task_id = max_id + 1
                
                # Initial refresh of all views
                self.refresh_task_list()
                self.update_today_tasks()
                
        except FileNotFoundError:
            print("DEBUG: No tasks.json file found, starting with empty task list")
            self.tasks = []
        except json.JSONDecodeError as e:
            print(f"DEBUG: Error decoding tasks.json: {e}")
            self.tasks = []
        except Exception as e:
            print(f"DEBUG: Unexpected error loading tasks: {e}")
            self.tasks = []

    def save_tasks(self):
        """Save tasks to JSON file"""
        with open('tasks.json', 'w') as f:
            json.dump(self.tasks, f, indent=4)
        self.status_bar.config(text="Tasks saved successfully")

    def refresh_task_list(self):
        """Update the task list display with colors"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter tasks based on current filters
        filtered_tasks = self.filter_tasks()
        
        # Configure tags for colors
        for priority, color in self.priority_colors.items():
            self.tree.tag_configure(priority, foreground=color)
        
        # Add tasks to tree with colors
        for task in filtered_tasks:
            priority = task.get('priority', 'Normal')
            item_id = self.tree.insert("", "end", 
                           values=(task['name'],
                                 task.get('category', 'Other'),
                                 priority,
                                 task['due_date'],
                                 task['status']),
                           tags=(priority,))
            
            # Add overdue highlighting
            if task['status'] != 'Completed':
                due_date = datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M")
                if due_date < datetime.now():
                    self.tree.tag_configure(f"overdue_{item_id}", background="#FFE6E6")
                    self.tree.item(item_id, tags=(priority, f"overdue_{item_id}"))
        
        # Update statistics after refreshing task list
        self.update_statistics()
        
        # Also update calendar view if it exists
        if hasattr(self, 'cal_task_list'):
            self.update_calendar_tasks()

    def filter_tasks(self):
        """Apply current filters to tasks"""
        filtered = self.tasks[:]
        print(f"\nDEBUG: Starting filter_tasks with {len(filtered)} tasks")
        
        try:
            # Print all tasks for debugging
            for task in filtered:
                print(f"DEBUG: Task before filtering - Name: {task['name']}, Due: {task['due_date']}, Status: {task.get('status')}, Priority: {task.get('priority', 'Normal')}")
            
            # Category filter
            if self.category_var.get() != "All":
                filtered = [t for t in filtered if t.get('category') == self.category_var.get()]
                print(f"DEBUG: After category filter: {len(filtered)} tasks")
            
            # Priority filter
            if self.priority_var.get() != "All":
                filtered = [t for t in filtered if t.get('priority', 'Normal') == self.priority_var.get()]
                print(f"DEBUG: After priority filter: {len(filtered)} tasks")
            
            # Status filter
            if self.status_var.get() != "All":
                filtered = [t for t in filtered if t.get('status', 'Pending') == self.status_var.get()]
                print(f"DEBUG: After status filter: {len(filtered)} tasks")
            
            # Due date filter
            if self.due_date_var.get() != "All":
                today = datetime.now().date()
                print(f"DEBUG: Today's date: {today}")
                filtered_by_date = []
                
                for task in filtered:
                    try:
                        # Parse task date properly
                        task_datetime = datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M")
                        task_date = task_datetime.date()
                        print(f"DEBUG: Checking task: {task['name']} with date {task_date}")
                        
                        if self.due_date_var.get() == "Today":
                            if task_date == today:
                                filtered_by_date.append(task)
                                print(f"DEBUG: Added task to today's list: {task['name']}")
                        elif self.due_date_var.get() == "This Week":
                            if 0 <= (task_date - today).days <= 7:
                                filtered_by_date.append(task)
                        elif self.due_date_var.get() == "This Month":
                            if task_date.year == today.year and task_date.month == today.month:
                                filtered_by_date.append(task)
                    except (ValueError, TypeError) as e:
                        print(f"DEBUG: Error parsing date for task: {task.get('name')} - {e}")
                        continue
                
                filtered = filtered_by_date
                print(f"DEBUG: After date filter: {len(filtered)} tasks")
            
            # Search filter
            if self.search_var.get():
                search_term = self.search_var.get().lower()
                filtered = [t for t in filtered if search_term in t['name'].lower()]
                print(f"DEBUG: After search filter: {len(filtered)} tasks")
            
            # Print remaining tasks after all filters
            print("DEBUG: Final filtered tasks:")
            for task in filtered:
                print(f"DEBUG: Remaining task - Name: {task['name']}, Due: {task['due_date']}, Status: {task.get('status')}, Priority: {task.get('priority', 'Normal')}")
            
            return filtered
        except Exception as e:
            print(f"DEBUG: Error in filter_tasks: {e}")
            return []

    def get_task_by_id(self, tree_id):
        """Get task dictionary from tree item ID"""
        values = self.tree.item(tree_id)['values']
        if values:
            # Find task by name and due date (assuming these are unique together)
            for task in self.tasks:
                if task['name'] == values[0] and task['due_date'] == values[3]:
                    return task
        return None

    def create_main_container(self):
        """Create the main container frame"""
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

    def create_header(self):
        """Create the header section"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(
            header_frame, 
            text="Tasks", 
            font=CustomStyle.HEADER_FONT
        ).pack(side=tk.LEFT)

    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Label(
            self.main_container, 
            text="Ready", 
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, padx=5, pady=2)

    def check_reminders(self):
        """Check for due reminders"""
        current_time = datetime.now()
        
        for task in self.tasks:
                due_time = datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M")
                if current_time >= due_time and task.get('id') not in self.active_reminders:
                    self.show_reminder(task)
        
        # Check again in 1 minute
        self.root.after(60000, self.check_reminders)

    def on_search(self, *args):
        """Handle search updates"""
        self.refresh_task_list()

    def on_task_select(self, event):
        """Handle task selection in the tree view"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        task = self.get_task_by_id(selected_items[0])
        if task:
            # Update details panel
            self.details_name.delete(0, tk.END)
            self.details_name.insert(0, task['name'])
            
            self.details_category.set(task.get('category', 'Other'))
            self.details_priority.set(task.get('priority', 'Normal'))
            self.details_date.delete(0, tk.END)
            self.details_date.insert(0, task['due_date'])
            
            self.reminder_enabled.set(task.get('reminder_enabled', False))
            self.reminder_time.set(task.get('reminder_time', '15 min'))
            
            self.notes_text.delete('1.0', tk.END)
            self.notes_text.insert('1.0', task.get('notes', ''))

            # Update reminder list
            self.update_reminder_list(task)

    def on_today_task_select(self, event):
        """Handle task selection in today's tasks view"""
        selected_items = self.today_tree.selection()
        if not selected_items:
            return
            
        # Get the selected task's values
        values = self.today_tree.item(selected_items[0])['values']
        if values:
            # Find the corresponding task
            task_name = values[0]
            task_time = values[1]
            
            # Get today's date
            today = datetime.now().strftime("%Y-%m-%d")
            task_datetime = f"{today} {task_time}"
            
            # Find matching task in main task list
            for task in self.tasks:
                if task['name'] == task_name and task['due_date'] == task_datetime:
                    # Switch to main tasks view and select the task
                    self.notebook.select(1)  # Switch to Tasks tab
                    self.select_task_in_tree(task)
                    break

    def edit_task(self, event):
        """Handle double-click on task item"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        task = self.get_task_by_id(selected_items[0])
        if task:
            self.show_edit_dialog(task)

    def delete_task(self, event=None):
        """Delete selected task"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            task = self.get_task_by_id(selected_items[0])
            if task:
                self.tasks.remove(task)
                self.save_tasks()
                self.refresh_task_list()
                self.status_bar.config(text="Task deleted successfully")

    def save_task_details(self):
        """Save changes from details panel"""
        # Get all values from the details panel
        task_data = {
            'name': self.details_name.get().strip(),
            'category': self.details_category.get().strip(),
            'priority': self.details_priority.get().strip(),
            'due_date': self.details_date.get().strip(),
            'reminder_enabled': self.reminder_enabled.get(),
            'reminder_time': self.reminder_time.get().strip(),
            'notes': self.notes_text.get('1.0', 'end-1c').strip(),
            'status': 'Pending'
        }
        
        # Validate required fields
        if not task_data['name'] or not task_data['due_date']:
            messagebox.showwarning("Invalid Input", "Please fill in task name and due date")
            return
        
        selected_items = self.tree.selection()
        
        if selected_items:  # Editing existing task
            task = self.get_task_by_id(selected_items[0])
            if task:
                task.update(task_data)
        else:  # Creating new task
            task_data['id'] = self.next_task_id
            self.next_task_id += 1
            self.tasks.append(task_data)
        
        # Save to file
        self.save_tasks()
        
        # Refresh display
        self.refresh_task_list()
        
        # Show success message
        self.status_bar.config(text="Task saved successfully")
        
        # Clear panel for next task
        if not selected_items:  # Only clear if it was a new task
            self.clear_details_panel()

    def show_date_picker(self):
        """Show calendar for date selection"""
        date_window = tk.Toplevel(self.root)
        date_window.title("Select Date")
        self.set_window_icon(date_window)  # Add icon
        
        cal = Calendar(date_window, selectmode='day',
                      year=datetime.now().year,
                      month=datetime.now().month,
                      day=datetime.now().day)
        cal.pack(pady=10)
        
        def set_date():
            selected_date = cal.get_date()
            current_time = datetime.now().strftime("%H:%M")
            self.details_date.delete(0, tk.END)
            self.details_date.insert(0, f"{selected_date} {current_time}")
            date_window.destroy()
        
        # Calendar button
        select_btn = CustomStyle.create_styled_button(
            date_window, "Select", set_date, "calendar"
        )
        select_btn.pack(pady=5)

    def show_reminder(self, task):
        """Show reminder dialog for a task"""
        task_id = task.get('id')
        if task_id is None:  # If task has no ID, assign one
            task_id = self.next_task_id
            task['id'] = task_id
            self.next_task_id += 1
            
        if task_id in self.active_reminders:
            return
            
        self.active_reminders[task_id] = True
        
        # Show system notification if enabled
        if self.settings.get('notification_enabled', True):
            self.show_system_notification(task)
        
        # Play sound if enabled
        if self.settings.get('sound_enabled', True):
            self.play_reminder_sound()
        
        # Create reminder window
        reminder = tk.Toplevel(self.root)
        reminder.title("Task Reminder")
        reminder.geometry("400x200")
        self.set_window_icon(reminder)  # Add icon
        
        # Bring window to front
        reminder.lift()
        reminder.focus_force()
        
        ttk.Label(reminder, text=f"Task: {task['name']}", font=CustomStyle.HEADER_FONT).pack(pady=10)
        ttk.Label(reminder, text=f"Due: {task['due_date']}").pack(pady=5)
        
        button_frame = ttk.Frame(reminder)
        button_frame.pack(pady=10)
        
        # Complete button
        complete_btn = CustomStyle.create_styled_button(
            button_frame, "Complete", 
            lambda: self.complete_task(task, reminder), "complete"
        )
        complete_btn.pack(side=tk.LEFT, padx=5)
        
        # Snooze button
        snooze_btn = CustomStyle.create_styled_button(
            button_frame, "Snooze",
            lambda: self.show_snooze_dialog(task['id']), "snooze"
        )
        snooze_btn.pack(side=tk.LEFT, padx=5)
        
        # Dismiss button
        dismiss_btn = CustomStyle.create_styled_button(
            button_frame, "Dismiss",
            reminder.destroy, "dismiss"
        )
        dismiss_btn.pack(side=tk.LEFT, padx=5)

    def show_system_notification(self, task):
        """Show system notification for task reminder"""
        try:
            notification.notify(
                title=self.app_name,  # Use app name instead of default
                message=f"Task: {task['name']}\nDue: {task['due_date']}",
                app_icon=self.icon_path,
                app_name=self.app_name,  # Add this line to set app name
                timeout=10,
            )
        except Exception as e:
            print(f"Failed to show notification: {e}")

    def update_calendar_tasks(self, event=None):
        """Update task list for selected calendar date"""
        # Get selected date in correct format
        selected_date = self.cal.get_date()
        # Convert date format if needed (depending on your calendar widget's output)
        date_parts = selected_date.split('/')
        if len(date_parts) == 3:
            # Convert MM/DD/YY to YYYY-MM-DD
            month, day, year = date_parts
            selected_date = f"20{year}-{month:>02}-{day:>02}"
        
        self.calendar_date_label.config(text=f"Tasks for {selected_date}")
        
        # Clear current items
        for item in self.cal_task_list.get_children():
            self.cal_task_list.delete(item)
        
        # Add tasks for selected date
        for task in self.tasks:
            if task['due_date'].startswith(selected_date):
                time = task['due_date'].split()[1]  # Get time part
                priority = task.get('priority', 'Normal')
                status = task.get('status', 'Pending')
                
                item_id = self.cal_task_list.insert(
                    "", "end",
                    values=(time, task['name'], priority, status)
                )
                
                # Apply priority color
                if priority in self.priority_colors:
                    self.cal_task_list.tag_configure(priority, foreground=self.priority_colors[priority])
                    self.cal_task_list.item(item_id, tags=(priority,))
        
        # Update display immediately
        self.cal_task_list.update()

    def show_edit_dialog(self, task):
        """Show dialog to edit task details"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Task")
        dialog.geometry("500x400")
        self.set_window_icon(dialog)  # Add icon
        
        # Task name
        ttk.Label(dialog, text="Task Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.insert(0, task['name'])
        name_entry.pack(pady=5)
        
        # Category
        ttk.Label(dialog, text="Category:").pack(pady=5)
        category_combo = ttk.Combobox(dialog, values=self.categories)
        category_combo.set(task.get('category', 'Other'))
        category_combo.pack(pady=5)
        
        # Priority
        ttk.Label(dialog, text="Priority:").pack(pady=5)
        priority_combo = ttk.Combobox(dialog, values=self.priorities)
        priority_combo.set(task.get('priority', 'Normal'))
        priority_combo.pack(pady=5)
        
        # Due date
        ttk.Label(dialog, text="Due Date (YYYY-MM-DD HH:MM):").pack(pady=5)
        date_entry = ttk.Entry(dialog, width=40)
        date_entry.insert(0, task['due_date'])
        date_entry.pack(pady=5)
        
        # Reminder
        reminder_var = tk.BooleanVar(value=task.get('reminder_enabled', False))
        ttk.Checkbutton(dialog, text="Enable Reminder", variable=reminder_var).pack(pady=5)
        
        # Notes
        ttk.Label(dialog, text="Notes:").pack(pady=5)
        notes_text = scrolledtext.ScrolledText(dialog, height=5)
        notes_text.insert('1.0', task.get('notes', ''))
        notes_text.pack(pady=5, fill=tk.BOTH, expand=True)
        
        def save_changes():
            # Get notes text properly
            notes_content = notes_text.get('1.0', 'end-1c')
            
            task.update({
                'name': name_entry.get(),
                'category': category_combo.get(),
                'priority': priority_combo.get(),
                'due_date': date_entry.get(),
                'reminder_enabled': reminder_var.get(),
                'notes': notes_content  # Make sure notes are saved
            })
            
            self.save_tasks()
            self.refresh_task_list()
            dialog.destroy()
            self.status_bar.config(text="Task updated successfully")
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10, fill=tk.X)
        
        ttk.Button(button_frame, text="Save", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def edit_calendar_task(self, event):
        """Edit task from calendar view"""
        selected_items = self.cal_task_list.selection()
        if not selected_items:
            return
            
        # Get task details
        values = self.cal_task_list.item(selected_items[0])['values']
        if values:
            selected_date = self.cal.get_date()
            task_time = values[0]
            task_name = values[1]
            
            # Find task in main task list
            for task in self.tasks:
                if (task['name'] == task_name and 
                    task['due_date'] == f"{selected_date} {task_time}"):
                    # Switch to tasks view and select the task
                    self.notebook.select(0)  # Switch to first tab (Tasks)
                    self.select_task_in_tree(task)
                    break

    def select_task_in_tree(self, task):
        """Select a specific task in the main tree view"""
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if values[0] == task['name'] and values[3] == task['due_date']:
                self.tree.selection_set(item)
                self.tree.see(item)
                self.on_task_select(None)
                break

    def sort_tasks(self, column):
        """Sort tasks by the specified column"""
        # Get all items from tree
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]
        
        # Store current sorting order
        if not hasattr(self, '_sort_reverse'):
            self._sort_reverse = {}
        self._sort_reverse[column] = not self._sort_reverse.get(column, False)
        
        # Sort items
        items.sort(reverse=self._sort_reverse[column])
        
        # Rearrange items in sorted order
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Update column header
        arrow = "↓" if self._sort_reverse[column] else "↑"
        
        for col in self.tree["columns"]:
            # Remove existing arrows from all headers
            text = self.tree.heading(col)["text"].rstrip(" ↑↓")
            # Add arrow to current sort column
            self.tree.heading(col, text=f"{text}{' ' + arrow if col == column else ''}")

    def complete_task(self, task, reminder_window=None):
        """Mark a task as completed and close its reminder window"""
        task['status'] = 'Completed'
        if task['id'] in self.active_reminders:
            del self.active_reminders[task['id']]
        
        # Close reminder window if provided
        if reminder_window:
            reminder_window.destroy()
        
        # Save and refresh
        self.save_tasks()
        self.refresh_task_list()
        self.status_bar.config(text=f"Task '{task['name']}' marked as completed")
        
        # Show completion notification
        if self.settings.get('notification_enabled', True):
            try:
                notification.notify(
                    title=f"{self.app_name} - Task Completed",  # Updated title
                    message=f"Task '{task['name']}' has been completed!",
                    app_icon=self.icon_path,
                    app_name=self.app_name,  # Add app name
                    timeout=5
                )
            except Exception as e:
                print(f"Failed to show completion notification: {e}")

    def clear_details_panel(self):
        """Clear all fields in the details panel for new task"""
        # Clear task name
        self.details_name.delete(0, tk.END)
        
        # Reset category and priority to defaults
        self.details_category.set("Other")
        self.details_priority.set("Normal")
        
        # Set due date to current time
        self.details_date.delete(0, tk.END)
        self.details_date.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        # Reset reminder settings
        self.reminder_enabled.set(False)
        self.reminder_time.set("15 min")
        
        # Clear notes
        self.notes_text.delete('1.0', tk.END)
        
        # Clear tree selection
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        
        self.status_bar.config(text="Ready to add new task")
        
        # Switch to Tasks tab when creating new task
        self.notebook.select(1)  # Index 1 is the Tasks tab

    def show_custom_reminder_dialog(self):
        """Show dialog for setting custom reminder"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Custom Reminder")
        dialog.geometry("400x600")
        self.set_window_icon(dialog)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Multiple reminders section
        reminder_type_frame = ttk.LabelFrame(dialog, text="Reminder Type")
        reminder_type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        reminder_type = tk.StringVar(value="single")
        ttk.Radiobutton(reminder_type_frame, text="Single Reminder", 
                       variable=reminder_type, value="single").pack(pady=2)
        ttk.Radiobutton(reminder_type_frame, text="Multiple Day Reminders", 
                       variable=reminder_type, value="multiple").pack(pady=2)
        
        # Container for reminder settings
        settings_container = ttk.Frame(dialog)
        settings_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Single reminder frame
        single_frame = ttk.Frame(settings_container)
        
        # Date selection
        date_frame = ttk.LabelFrame(single_frame, text="Reminder Date")
        date_frame.pack(fill=tk.X, pady=5)
        
        cal = Calendar(date_frame, selectmode='day',
                      year=datetime.now().year,
                      month=datetime.now().month,
                      day=datetime.now().day)
        cal.pack(pady=5)
        
        # Multiple days frame
        multiple_frame = ttk.Frame(settings_container)
        days_frame = ttk.LabelFrame(multiple_frame, text="Select Days")
        days_frame.pack(fill=tk.X, pady=5)
        
        # Days before due date
        days_vars = []
        for i in range(7):
            var = tk.BooleanVar(value=False)
            days_vars.append(var)
            ttk.Checkbutton(days_frame, 
                          text=f"{i+1} day{'s' if i > 0 else ''} before due date",
                          variable=var).pack(anchor=tk.W, padx=5, pady=2)
        
        # Time selection (shared between single and multiple)
        time_frame = ttk.LabelFrame(dialog, text="Reminder Time")
        time_frame.pack(fill=tk.X, padx=5, pady=5)
        
        hour_var = tk.StringVar(value=datetime.now().strftime("%H"))
        minute_var = tk.StringVar(value=datetime.now().strftime("%M"))
        
        time_entry_frame = ttk.Frame(time_frame)
        time_entry_frame.pack(pady=5)
        
        ttk.Label(time_entry_frame, text="Hour:").pack(side=tk.LEFT)
        hours = ttk.Spinbox(time_entry_frame, from_=0, to=23, width=5, 
                          textvariable=hour_var)
        hours.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(time_entry_frame, text="Minute:").pack(side=tk.LEFT)
        minutes = ttk.Spinbox(time_entry_frame, from_=0, to=59, width=5, 
                            textvariable=minute_var)
        minutes.pack(side=tk.LEFT, padx=5)
        
        def update_view(*args):
            if reminder_type.get() == "single":
                multiple_frame.pack_forget()
                single_frame.pack(fill=tk.BOTH, expand=True)
            else:
                single_frame.pack_forget()
                multiple_frame.pack(fill=tk.BOTH, expand=True)
        
        reminder_type.trace('w', update_view)
        update_view()  # Initial view
        
        def set_custom_reminder():
            selected_time = f"{hour_var.get()}:{minute_var.get()}"
            reminder_dates = []
            
            if reminder_type.get() == "single":
                selected_date = cal.get_date()
                date_parts = selected_date.split('/')
                if len(date_parts) == 3:
                    month, day, year = date_parts
                    selected_date = f"20{year}-{month:>02}-{day:>02}"
                reminder_dates.append(f"{selected_date} {selected_time}")
            else:
                # Get due date from task or current selection
                task = None
                selected_items = self.tree.selection()
                if selected_items:
                    task = self.get_task_by_id(selected_items[0])
                
                if task:
                    due_date = datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M")
                    for i, var in enumerate(days_vars):
                        if var.get():
                            reminder_date = due_date - timedelta(days=i+1)
                            reminder_dates.append(
                                f"{reminder_date.strftime('%Y-%m-%d')} {selected_time}"
                            )
            
            # Store reminder settings
            custom_reminder = {
                'type': reminder_type.get(),
                'times': reminder_dates,
                'time': selected_time
            }
            
            # Update task
            selected_items = self.tree.selection()
            if selected_items:
                task = self.get_task_by_id(selected_items[0])
                if task:
                    task.update({
                        'reminder_enabled': True,
                        'reminder_time': 'custom',
                        'custom_reminder': custom_reminder
                    })
                    self.save_tasks()
            
            dialog.destroy()
            messagebox.showinfo("Success", 
                              f"Reminder{'s' if len(reminder_dates)>1 else ''} set for:\n" + 
                              "\n".join(reminder_dates))
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        # Save button
        save_btn = CustomStyle.create_styled_button(
            button_frame, "Set Reminder", set_custom_reminder, "save"
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = CustomStyle.create_styled_button(
            button_frame, "Cancel", dialog.destroy, "dismiss"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def delete_reminder(self):
        """Delete selected reminder from task"""
        selected_reminder = self.reminder_list.selection()
        if not selected_reminder:
            return
            
        selected_task = self.tree.selection()
        if not selected_task:
            return
            
        task = self.get_task_by_id(selected_task[0])
        if task and 'custom_reminder' in task:
            reminder_date = self.reminder_list.item(selected_reminder[0])['values']
            reminder_datetime = f"{reminder_date[0]} {reminder_date[1]}"
            
            # Remove from times list
            task['custom_reminder']['times'] = [
                t for t in task['custom_reminder']['times'] 
                if t != reminder_datetime
            ]
            
            # If no reminders left, disable reminders for task
            if not task['custom_reminder']['times']:
                task['reminder_enabled'] = False
                task['reminder_time'] = ''
                del task['custom_reminder']
            
            self.save_tasks()
            self.update_reminder_list(task)
            messagebox.showinfo("Success", "Reminder deleted successfully")

    def update_reminder_list(self, task):
        """Update the reminder list display for selected task"""
        # Clear current items
        for item in self.reminder_list.get_children():
            self.reminder_list.delete(item)
            
        if not task:
            return
            
        # Add reminders to list
        if task.get('reminder_time') == 'custom' and 'custom_reminder' in task:
            for reminder_time in task['custom_reminder']['times']:
                date, time = reminder_time.split(' ')
                self.reminder_list.insert("", "end", values=(date, time))
        elif task.get('reminder_enabled'):
            # Show standard reminder if enabled
            due_date = datetime.strptime(task['due_date'], "%Y-%m-%d %H:%M")
            self.reminder_list.insert("", "end", 
                                    values=(due_date.strftime("%Y-%m-%d"),
                                          due_date.strftime("%H:%M")))


    def create_system_tray(self):
        """Create system tray icon and menu"""
        if not hasattr(self, 'tray_icon'):
            try:
                from pystray import Icon, Menu, MenuItem
                import PIL.Image
                
                # Load icon
                image = PIL.Image.open(self.icon_path)
                
                # Create menu
                menu = Menu(
                    MenuItem("Show", self.show_window),
                    MenuItem("Exit", self.quit_app)
                )
                
                # Create tray icon
                self.tray_icon = Icon("TaskReminder", image, "Task Reminder", menu)
                
                # Start tray icon in separate thread
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
            except Exception as e:
                print(f"Failed to create system tray icon: {e}")

    def show_window(self):
        """Show and restore window"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self):
        """Clean exit application"""
        try:
            if hasattr(self, 'tray_icon'):
                self.tray_icon.stop()
        except:
            pass
        self.root.quit()

if __name__ == "__main__":
    root = ThemedTk()
    app = TaskReminder(root)
    root.mainloop()

