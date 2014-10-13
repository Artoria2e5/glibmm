class GirPrinter:
    def __init__(self, parser):
        self._parser = parser

    @staticmethod
    def _print_single_enumeration(enum_object):
        if enum_object.is_flag:
            enum_type = "flags"
        else:
            enum_type = "enum"

        print("(define-" + enum_type + "-extended " + enum_object.name)
        print("  (in-module \"" + enum_object.module + "\")")
        print("  (c-name \"" + enum_object.c_name + "\")")
        print("  (values")

        for member in enum_object.members:
            print("    '(\"" + member.name + "\" " +
                  "\"" + member.c_name + "\" " +
                  "\"" + member.value + "\")")
        print("  )")
        print(")\n")

    def print_enumerations(self):
        for enumeration in self._parser.get_enumerations():
            GirPrinter._print_single_enumeration(enumeration)
