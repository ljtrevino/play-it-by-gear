from kivy.graphics import Color

def hex_to_rgb(hex):
    rgb = tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    return tuple(v/255.0 for v in rgb)

colors = {
            'b' : Color(rgb=hex_to_rgb('#56BDCD')),
            'g' : Color(rgb=hex_to_rgb('#95CB5F')),
            'y' : Color(rgb=hex_to_rgb('#FED766')),
            'r' : Color(rgb=hex_to_rgb('#EC5451')),
            'red' : Color(rgb=hex_to_rgb('#EC5451')),
            'orange' : Color(rgb=hex_to_rgb('#FFA617')),
            'yellow' : Color(rgb=hex_to_rgb('#FED766')),
            'green' : Color(rgb=hex_to_rgb('#95CB5F')),
            'blue' : Color(rgb=hex_to_rgb('#56BDCD')),
            'purple' : Color(rgb=hex_to_rgb('#B98DD1')),
            'dark_brown': Color(rgb=(150/255, 127/255, 101/255)),
            'light_brown': Color(rgb=(186/255, 158/255, 126/255)),
            'grey': Color(rgb=hex_to_rgb('#5e6f81')),
            'dark_grey': Color(rgb=hex_to_rgb('#485564')),
            'trout': Color(rgb=hex_to_rgb('#8796a7')),

            'light_red' : Color(rgb=hex_to_rgb('#f8bdbb')),
            'light_orange' : Color(rgb=hex_to_rgb('#ffe1b3')),
            'light_yellow' : Color(rgb=hex_to_rgb('#fff0c7')),
            'light_purple' : Color(rgb=hex_to_rgb('#e3d3ed')),
         }
