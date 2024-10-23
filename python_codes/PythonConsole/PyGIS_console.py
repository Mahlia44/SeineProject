from qgis.core import QgsProject
from collections import Counter
import numpy as np

#QgsProject.instance().clear()

# Get the home path of the project
home_path = QgsProject.instance().homePath()


# Get the layer by its name
layer  = QgsProject.instance().mapLayersByName('Intersection')[0]
"""
for feature in layer.getFeatures():
    area_type = feature.geometry().area()
    
    print("Feature ID:", feature.id(), "- Area_Ha:", area_ha, "- Area_Type:", area_type)



# Start editing the layer
layer.startEditing()
for feature in layer.getFeatures():
    area_type = feature.geometry().area()
    area_ha = feature['Area_Ha']
    if area_ha != 0:
        ratio = area_type / area_ha
    else:
        ratio = 0
    layer.dataProvider().changeAttributeValues({feature.id(): {layer.fields().indexFromName("Area_Ratio"): ratio}})
    
# Commit changes and stop editing
layer.commitChanges()
layer.stopEditing()"""

if not layer.isValid():
    print("Layer failed to load!")
else:
    # Start editing the layer
    layer.startEditing()
   
    # Get the index of the new attribute field
    field_index = layer.fields().indexFromName("Geom_Area")
    
    # Iterate over features and calculate the area of each geometry
    for feature in layer.getFeatures():
        # Get the geometry of the feature
        geometry = feature.geometry()
        # Calculate the area of the geometry
        area = geometry.area()
        # Set the calculated area value to the new attribute
        layer.dataProvider().changeAttributeValues({feature.id(): {field_index: area}})
    
    # Commit changes and stop editing
    layer.commitChanges()
    

