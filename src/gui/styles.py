"""
Centralized styling constants for the application UI.
"""

class AppStyles:
    """Central class for all application styling constants."""
    
    # Colors
    PRIMARY_COLOR = "#3498db"
    PRIMARY_DARK = "#2980b9"
    PRIMARY_DARKER = "#1f648b"
    TEXT_PRIMARY = "#2c3e50"
    TEXT_SECONDARY = "#7f8c8d"
    BACKGROUND = "#ecf0f1"
    GROUP_BACKGROUND = "#ffffff"
    BORDER_COLOR = "#bdc3c7"
    
    # Typography
    HEADER_SIZE = "24px"
    HEADER_WEIGHT = "bold"
    DESCRIPTION_SIZE = "14px" 
    DESCRIPTION_WEIGHT = "normal"
    GROUP_TITLE_SIZE = "16px"
    GROUP_TITLE_WEIGHT = "600"
    FORM_LABEL_SIZE = "12px"
    BUTTON_TEXT_SIZE = "14px"
    
    # Spacing
    MARGIN = "20px"
    SPACING = "15px"
    GROUP_PADDING = "15px"
    
    # Sizes
    BUTTON_HEIGHT = "32px"
    BUTTON_MIN_WIDTH = "150px"
    SIDEBAR_WIDTH = "250px"
    
    # Style sheets
    @classmethod
    def get_button_style(cls, primary=True):
        """Return a button style sheet."""
        if primary:
            return f"""
                background-color: {cls.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: {cls.BUTTON_TEXT_SIZE};
                font-weight: medium;
                border-radius: 4px;
                height: {cls.BUTTON_HEIGHT};
            """
        else:
            return f"""
                background-color: white;
                color: {cls.TEXT_PRIMARY};
                border: 1px solid {cls.BORDER_COLOR};
                padding: 8px 16px;
                font-size: {cls.BUTTON_TEXT_SIZE};
                font-weight: medium;
                border-radius: 4px;
                height: {cls.BUTTON_HEIGHT};
            """
    
    @classmethod
    def get_header_style(cls):
        """Return header style."""
        return f"""
            font-size: {cls.HEADER_SIZE};
            font-weight: {cls.HEADER_WEIGHT};
            color: {cls.TEXT_PRIMARY};
            margin-bottom: 10px;
        """
    
    @classmethod
    def get_description_style(cls):
        """Return description style."""
        return f"""
            font-size: {cls.DESCRIPTION_SIZE};
            color: {cls.TEXT_SECONDARY};
            margin-bottom: 15px;
        """
    
    @classmethod
    def get_group_box_style(cls):
        """Return group box style."""
        return f"""
            font-size: {cls.GROUP_TITLE_SIZE};
            font-weight: {cls.GROUP_TITLE_WEIGHT};
            background-color: {cls.GROUP_BACKGROUND};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 5px;
            padding-top: 20px;
            margin-top: 10px;
        """ 