import arcpy
import pythonaddins

workspace = arcpy.env.workspace
desc = arcpy.Describe(workspace)
path_workspace = desc.path
poligon_path = path_workspace
czesc_wspolna = path_workspace + "\czesc_wspolna.shp"
kopia_oryginalu = path_workspace + "\kopia_oryginalu.shp"


mxd = arcpy.mapping.MapDocument("Current")
list_layers = arcpy.mapping.ListLayers(mxd)
l = len(list_layers)


if l == 0:
    print("koniecznie wczytaj warswy i koniecznie wybierz opcje")
else:
    while l != 1:
        list_layers.pop()
        l = len(list_layers)
    print("domyslnie wybrana jest najwyzsza warstwa")
    print(str(list_layers))


class rysuj_poligon(object):
    """Implementation for PAG_PROJEKT_addin.tool (Tool)"""

    def __init__(self):
        self.enabled = True
        self.shape = "Line"  # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing and to activate the onLine/Polygon/Circle event sinks.
        self.cursor = 3

    def onLine(self, line_geometry):

        if arcpy.Exists(poligon_path + "\poligon.shp"):
            arcpy.Delete_management(poligon_path + "\poligon.shp")

        arcpy.CreateFeatureclass_management(poligon_path, "poligon", "POLYGON")

        array = arcpy.Array()
        part = line_geometry.getPart(0)
        for pt in part:
            array.add(pt)
        array.add(line_geometry.firstPoint)

        polygon_obj = arcpy.Polygon(array)

        path_fc = poligon_path + "\poligon.shp"
        cursor = arcpy.da.InsertCursor(path_fc, ['Shape@'])
        cursor.insertRow([polygon_obj])
        del cursor

        for l in list_layers:
            if arcpy.Exists(czesc_wspolna):
                arcpy.Delete_management(czesc_wspolna)

            arcpy.Intersect_analysis([l, "poligon"], czesc_wspolna, "", "", "INPUT")

            if arcpy.Exists(kopia_oryginalu):
                arcpy.Delete_management(kopia_oryginalu)

            desc = arcpy.Describe(l)
            print desc
            path = desc.path
            print path
            kopia_oryginalu_sciezka = path + '\\' + str(l) + ".shp"
            print kopia_oryginalu_sciezka
            arcpy.Copy_management(kopia_oryginalu_sciezka, kopia_oryginalu)
            arcpy.Delete_management(kopia_oryginalu_sciezka)
            try:
                arcpy.SymDiff_analysis(kopia_oryginalu, "czesc_wspolna", kopia_oryginalu_sciezka, "ONLY_FID", 0.01)
            except Exception as e:
                print(e)
                arcpy.Copy_management(kopia_oryginalu,
                                      kopia_oryginalu_sciezka)
                print("sprobuj jeszcze raz")
        for df in arcpy.mapping.ListDataFrames(mxd):
            for lyr in arcpy.mapping.ListLayers(mxd, "", df):
                if lyr.name.lower() in ["poligon", "kopia_oryginalu", "czesc_wspolna"]:
                    arcpy.mapping.RemoveLayer(df, lyr)


class tnij_najwyzsza(object):
    """Implementation for PAG_PROJEKT_addin.button (Button)"""

    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        print("wybrales opcje z tnij najwyzsza warstwe")
        global list_layers
        list_layers = arcpy.mapping.ListLayers(mxd)
        l = len(list_layers)
        while l != 1:
            list_layers.pop()
            l = len(list_layers)

        print("najwyzsza wartwa to : " + str(list_layers))


class tnij_wszystkie(object):
    """Implementation for PAG_PROJEKT_addin.button_1 (Button)"""

    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        print("wybrales opcje z tnij wszystkie warstwy")
        global list_layers
        list_layers = arcpy.mapping.ListLayers(mxd)
        print("wszystkie wartwy to : " + str(list_layers))


class wlacz(object):
    """Implementation for AG_PAG_addin.button_2 (Button)"""

    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool.enabled = True


class wylacz(object):
    """Implementation for AG_PAG_addin.button_3 (Button)"""

    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        tool.enabled = False
