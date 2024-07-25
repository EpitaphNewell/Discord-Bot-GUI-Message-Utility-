<img src="https://i.ibb.co/CByKFr5/16-1.png" alt="16-1" border="0" />

# Documentation for Using JSON to Create Application Styles

This documentation explains how to use a JSON file to customize the styles of your Python application using Tkinter. You can change the appearance of various interface elements such as text areas, buttons, and user lists.

## Style File

The style file should be in JSON format and stored in the `css` folder with the name `style.json`. Below is the structure of the file and the description of the available settings:

### File Structure

```json
{
    "console": {
        "bg": "#FFFFFF",
        "fg": "#000000",
        "url_fg": "blue"
    },
    "entry": {
        "bg": "#FFFFFF",
        "fg": "#000000"
    },
    "button": {
        "bg": "#0078d4",
        "fg": "#FFFFFF",
        "font": "Arial 10 bold"
    },
    "listbox": {
        "bg": "#FFFFFF",
        "fg": "#000000"
    }
}
```
# Parameter Descriptions
- console: Style for the text area (ScrolledText).

- bg (Background): Background color of the text area. Example: #FFFFFF (white).
- fg (Text): Text color in the text area. Example: #000000 (black).
- url_fg (URL Color): Color for links in the text area. Example: blue.
- entry: Style for the text field (Entry).

- bg (Background): Background color of the text field. Example: #FFFFFF (white).
- fg (Text): Text color in the text field. Example: #000000 (black).
- button: Style for buttons (Button).

- bg (Background): Background color of the buttons. Example: #0078d4 (blue).
- fg (Text): Text color on the buttons. Example: #FFFFFF (white).
- font (Font): Font and size of the text on the buttons. Example: Arial 10 bold.
- listbox: Style for the user list (Listbox).

- bg (Background): Background color of the list. Example: #FFFFFF (white).
- fg (Text): Text color in the list. Example: #000000 (black).

# Applying Styles
1. Create a JSON File: Create a style.json file in the css folder of your project.
2. Configure Parameters: Edit the parameters in the JSON file according to your preferences.
3. Run the Application: When the application starts, the styles will be automatically applied to the interface elements if the style.json file exists.
4. Check and Debug: Ensure that all styles are applied correctly and edit the JSON file as needed.
# Example Code
```json
{
    "console": {
        "bg": "#000000",
        "fg": "#FFFFFF",
        "font": "Courier New 12"
    },
    "entry": {
        "bg": "#333333",
        "fg": "#FFFFFF",
        "font": "Arial 12"
    },
    "button": {
        "bg": "#4CAF50",
        "fg": "#FFFFFF",
        "font": "Arial 10 bold"
    },
    "listbox": {
        "bg": "#444444",
        "fg": "#FFFFFF",
        "font": "Arial 12"
    }
}
```
