import xml.dom.minidom


def is_attribute_set(xml_node, attribute_name, expected_value):
    return True if xml_node.hasAttribute(attribute_name) and xml_node.getAttribute(
        attribute_name) == expected_value else False


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


class Documentation:
    def __init__(self, xml_root):
        self.content = xml_root  # .data todo


class InterfaceObjectInfo(ObjectInfo):
    def __init__(self, xml_root, module):
        self.module = module


class ClassObjectInfo(ObjectInfo):
    def __init__(self, xml_root, module):
        ObjectInfo.__init__(self, xml_root.getAttribute("name"), xml_root.getAttribute("c:type"))
        self.module = module
        self.parent = xml_root.getAttribute("parent") if xml_root.hasAttribute("parent") else None
        self.interfaces = []

        for value in xml_root.childNodes:
            if value.nodeType == xml.dom.Node.ELEMENT_NODE:
                if value.tagName == "doc":
                    self._doc = Documentation(value)
                elif value.tagName == "implements":
                    self.interfaces.append(InterfaceObjectInfo(value, module))
                elif value.tagName == "constructor":
                    0  # todo
                elif value.tagName == "method":
                    0  # todo
                elif value.tagName == "property":
                    0  # todo
                elif value.tagName == "field":
                    0  # todo


class RecordInfo(ObjectInfo):
    def __init__(self, xml_root, module):
        ObjectInfo.__init__(self, xml_root.getAttribute("name"), xml_root.getAttribute("c:type"))
        self.module = module
        self.deprecated = is_attribute_set(xml_root, "deprecated", 1)
        self.fields = []
        self.functions = []

        for value in xml_root.childNodes:
            if value.nodeType == xml.dom.Node.ELEMENT_NODE:
                if value.tagName == "field":
                    self.fields.append(FieldInfo(value))
                elif value.tagName == "constructor" or value.tagName == "function" or value.tagName == "method":
                    self.functions.append(FunctionInfo(value))


class FunctionInfo(ObjectInfo):
    def __init__(self, xml_root):
        ObjectInfo.__init__(self, xml_root.getAttribute("name"), xml_root.getAttribute("c:identifier"))
        self.returnValue = None
        self.type = xml_root.getAttribute("type") if xml_root.hasAttribute("type") else None
        self.is_deprecated = is_attribute_set(xml_root, "deprecated", 1)
        self.is_throwable = is_attribute_set(xml_root, "throws", "1")
        self.parameters = []
        self.has_instance_parameter = False
        self.is_constructor = xml_root.tagName == "constructor"
        i = 0
        for value in xml_root.childNodes:
            i += 1
            if value.nodeType == xml.dom.Node.ELEMENT_NODE:
                if value.tagName == "return-value":
                    self.returnValue = ReturnValueInfo(value)
                elif value.tagName == "parameters":
                    for param in value.childNodes:
                        if param.nodeType == xml.dom.Node.ELEMENT_NODE:
                            if param.tagName == "parameter":
                                self.parameters.append(FunctionParameterInfo(param))
                            elif param.tagName == "instance-parameter":
                                self.has_instance_parameter = True


class FunctionParameterInfo():
    def __init__(self, xml_root):
        self.transfer_ownership = xml_root.getAttribute("transfer-ownership") if xml_root.hasAttribute(
            "transfer-ownership") else None
        self.name = xml_root.getAttribute("name")
        self.type = None
        self.doc = None

        for value in xml_root.childNodes:
            if value.nodeType == xml.dom.Node.ELEMENT_NODE:
                if value.tagName == "type" or value.tagName == "array":
                    self.type = TypeInfo(value)
                elif value.tagName == "doc":
                    self.doc = Documentation(value)


class ReturnValueInfo():
    def __init__(self, xml_root):
        self.is_allow_none = is_attribute_set(xml_root, "allow-none", 1)
        self.is_skip = is_attribute_set(xml_root, "skip", 1)
        self.transfer_ownership = xml_root.getAttribute("transfer-ownership") if xml_root.hasAttribute(
            "transfer-ownership") else None
        self.returnType = None
        self.doc = None

        for value in xml_root.childNodes:
            if value.nodeType == xml.dom.Node.ELEMENT_NODE:
                if value.tagName == "type" or value.tagName == "array":
                    self.returnType = TypeInfo(value)
                    if self.returnType.c_name == "void":
                        self.returnType.c_name = "none"
                elif value.tagName == "doc":
                    self.doc = Documentation(value)


class FieldInfo():
    def __init__(self, xml_root):
        self.name = xml_root.getAttribute("name")
        self.is_writable = is_attribute_set(xml_root, "writable", 1)
        self.is_readable = is_attribute_set(xml_root, "readable", 1)
        self.is_private = is_attribute_set(xml_root, "private", 1)

        self.type = None
        self.documentation = None

        for value in xml_root.childNodes:
            if value.nodeType == xml.dom.Node.ELEMENT_NODE:
                if value.tagName == "type":
                    self.type = TypeInfo(value)
                elif value.tagName == "doc":
                    self.documentation = Documentation(value)


class TypeInfo(ObjectInfo):
    def __init__(self, xml_root):
        ctpe = xml_root.getAttribute("c:type").replace(" ", "-")
        if xml_root.tagName == "array" and\
                not ctpe.startswith("gconst") and not ctpe.startswith("const") \
                and not is_attribute_set(xml_root.parentNode, "direction", "out")\
                and not is_attribute_set(xml_root.parentNode, "direction", "inout"):
            ctpe = "const-" + ctpe
        ObjectInfo.__init__(self, xml_root.getAttribute("type"), ctpe)
        self.subtypes = []
        for value in xml_root.childNodes:
            if value.nodeType == xml.dom.Node.ELEMENT_NODE:
                if value.tagName == "type":
                    self.subtypes.append(TypeInfo(value))


class GirParser:
    def __init__(self):
        self._enums = []
        self._records = []

    def parse_file(self, gir_file):
        document = xml.dom.minidom.parse(gir_file)
        for namespace in document.documentElement.getElementsByTagName('namespace'):
            module = namespace.getAttribute("c:identifier-prefixes")
            for element in namespace.childNodes:
                if element.nodeType == xml.dom.Node.ELEMENT_NODE:
                    if element.tagName in ["enumeration", "bitfield"]:
                        self._enums.append(EnumObjectInfo(element, module))
                    elif element.tagName == "record":
                        self._records.append(RecordInfo(element, module))

    def get_enumerations(self):
        return self._enums

    def get_records(self):
        return self._records
