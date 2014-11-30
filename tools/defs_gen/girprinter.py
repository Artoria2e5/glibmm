class GirPrinter:
    def __init__(self, parser):
        self._parser = parser

    @staticmethod
    def _print_single_method(method_object, parent, nam):
        # todo do it better, move it to method's class maybe..
        is_static = False
        if len(method_object.parameters) + method_object.is_throwable > 0:
            i = 0
            for param in method_object.parameters:
                if param.type is not None and nam == param.type.name and i == 0:
                    is_static = True
                i += 1

        if is_static or method_object.has_instance_parameter:
            print("(define-method " + method_object.name)
            print("  (of-object \"" + parent + "\")")
        else:
            print("(define-function " + method_object.name)
        print("  (c-name \"" + method_object.c_name + "\")")
        ret = method_object.returnValue.returnType.c_name if method_object.returnValue.returnType is not None else "void"
        print("  (return-type \"" + ret + "\")")

        if len(method_object.parameters) + method_object.is_throwable > 0:
            print("  (parameters")
            i = 0
            for param in method_object.parameters:
                if param.type is not None:
                    print("    '(\"" + param.type.c_name + "\" \"" + param.name + "\")")
            if method_object.is_throwable == 1:
                print("    '(\"GError**\" \"error\")")
            print("  )")
        print(")")
        print("")

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

    def print_methods(self):
        for record in self._parser.get_records():
            for method in record.functions:
                if method.has_instance_parameter or method.is_constructor:
                    GirPrinter._print_single_method(method, record.c_name, record.name)
