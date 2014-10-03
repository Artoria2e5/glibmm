import xml.dom.minidom


class EnumMember:
    def __init__(self, name, c_name, value):
        self.name = name
        self.c_name = c_name
        self.value = value


class EnumObject:
    def __init__(self, xml_root, module):
        self.type_name = xml_root.getAttribute("name")
        self.is_flag = self.type_name.endswith("Flags")
        self.c_type_name = xml_root.getAttribute("c:type")
        self.module = module
        self.members = []

        for value in xml_root.childNodes:
            if value.nodeType == xml.dom.Node.ELEMENT_NODE and value.tagName == "member":
                self.members.append(
                    EnumMember(
                        value.getAttribute("name"),
                        value.getAttribute("c:identifier"),
                        value.getAttribute("value")))


class GirParser:
    def __init__(self):
        self._enums = []

    def parse_file(self, gir_file):
        print("trying to parse", gir_file)
        document = xml.dom.minidom.parse(gir_file)
        for namespace in document.documentElement.getElementsByTagName('namespace'):
            module = namespace.getAttribute("c:identifier-prefixes")
            for element in namespace.childNodes:
                if element.nodeType == xml.dom.Node.ELEMENT_NODE and \
                        (element.tagName == "enumeration" or element.tagName == "bitfield"):
                    self._enums.append(EnumObject(element, module))

    def get_enumerations(self):
        return self._enums
