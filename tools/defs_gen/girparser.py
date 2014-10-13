import xml.dom.minidom


class ObjectInfo:
    def __init__(self, type_name, c_type_name):
        self.name = type_name
        self.c_name = c_type_name


class EnumMemberInfo(ObjectInfo):
    def __init__(self, type_name, c_type_name, value):
        ObjectInfo.__init__(self, type_name, c_type_name)
        self.value = value


class EnumObjectInfo(ObjectInfo):
    def __init__(self, xml_root, module):
        ObjectInfo.__init__(self, xml_root.getAttribute("name"), xml_root.getAttribute("c:type"))
        self.is_flag = self.name.endswith("Flags")
        self.module = module
        self.members = []

        for value in xml_root.childNodes:
            if value.nodeType == xml.dom.Node.ELEMENT_NODE and value.tagName == "member":
                self.members.append(
                    EnumMemberInfo(
                        value.getAttribute("name"),
                        value.getAttribute("c:identifier"),
                        value.getAttribute("value")))


class ReturnValueInfo(ObjectInfo):
    def __init__(self, type_name, c_type_name):
        ObjectInfo.__init__(type_name, c_type_name)


class MethodParameterInfo(ObjectInfo):
    def __init__(self, xml_root):
        self.name = xml_root.getAttribute("name")
        for type_info in xml_root.getElementsByTagName("type"):
            ObjectInfo.__init__(self, type_info.getAttribute("name"), type_info.getAttribute("c:type"))
            break


class MethodObjectInfo:
    def __init__(self, xml_root):
        self.name = xml_root.getAttribute("name")
        self.c_name = xml_root.getAttribute("c:identifier")
        self.parameters = []

        for return_xml in xml_root.getElementsByTagName("return-value"):
            self.return_type = return_xml.get_name
            break


class ClassObject:
    def __init__(self, xml_root, module):
        self.type_name = xml_root.getAttribute("name")
        self.c_type_name = xml_root.getAttribute("c:type")
        self.module = module


class GirParser:
    def __init__(self):
        self._enums = []

    def parse_file(self, gir_file):
        document = xml.dom.minidom.parse(gir_file)
        for namespace in document.documentElement.getElementsByTagName('namespace'):
            module = namespace.getAttribute("c:identifier-prefixes")
            for element in namespace.childNodes:
                if element.nodeType == xml.dom.Node.ELEMENT_NODE and \
                        (element.tagName == "enumeration" or element.tagName == "bitfield"):
                    self._enums.append(EnumObjectInfo(element, module))

    def get_enumerations(self):
        return self._enums
