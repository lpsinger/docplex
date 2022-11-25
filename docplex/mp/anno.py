# --------------------------------------------------------------------------
# Source file provided under Apache License, Version 2.0, January 2004,
# http://www.apache.org/licenses/
# (c) Copyright IBM Corp. 2015, 2022
# --------------------------------------------------------------------------

# gendoc: ignore
import sys
from io import StringIO

from docplex.mp.constants import CplexScope
from docplex.mp.utils import OutputStreamAdapter


class ModelAnnotationPrinter(object):
    # header contains the final newline
    mst_header = """<?xml version = "1.0" standalone="yes"?>
"""
    anno_extension = ".ann"

    annotations_start_tag = "<CPLEXAnnotations>\n"
    annotations_end_tag   = "</CPLEXAnnotations>\n"
    benders_start_tag     = " <CPLEXAnnotation name='cpxBendersPartition' type='long' default='0'>\n"
    benders_end_tag       = " </CPLEXAnnotation>\n"

    # map to cplex annotation object types
    cplex_anno_objtype_map = {CplexScope.VAR_SCOPE: 1,
                              CplexScope.LINEAR_CT_SCOPE: 2,
                              CplexScope.SOS_SCOPE: 3,
                              CplexScope.IND_CT_SCOPE: 4,
                              CplexScope.QUAD_CT_SCOPE: 5}

    @staticmethod
    def print_signature(out):
        from docplex.version import docplex_version_string
        osa = OutputStreamAdapter(out)
        osa.write("<?xml version='1.0' encoding='utf-8'?>\n")
        osa.write("<!-- This file has been generated by DOcplex version {}  -->\n".format(docplex_version_string))

    @classmethod
    def _anno_name(cls, cpxscope, obj_name, obj_index):
        if obj_name is not None:
            return obj_name
        else:
            return '%s%d' % (cpxscope.prefix, obj_index)

    @classmethod
    def print(cls, out, model):
        osa = OutputStreamAdapter(out)

        cls.print_signature(out)
        # <CPLEXSolution version="1.0">
        osa.write(cls.annotations_start_tag)

        osa.write(cls.benders_start_tag)
        for cplex_scope, annotated in model.get_annotations_by_scope().items():
            anno_objtype = cls.cplex_anno_objtype_map.get(cplex_scope)
            if anno_objtype is not None and annotated:
                osa.write("  <object type='{0:d}'>\n".format(anno_objtype))
                for obj, benders_value in annotated:                   # FIXME: what if no name??
                    obj_index = obj.index  # not checked
                    anno_name = cls._anno_name(cplex_scope, obj.name, obj_index)
                    if obj_index >= 0:
                        # ignore objects not added to the model
                        osa.write("   <anno name='{0}' index='{1:d}' value='{2:d}'/>\n".format(anno_name, obj_index, benders_value))
                osa.write('  </object>\n')
        #  </CPLEXAnnotations>
        osa.write(cls.benders_end_tag)
        osa.write(cls.annotations_end_tag)
        osa.write('\n')

    @classmethod
    def print_to_stream(cls, mdl, out, extension=anno_extension):
        if out is None:
            # prints on standard output
            cls.print(sys.stdout, mdl)
        elif isinstance(out, str):
            # a string is interpreted as a path name
            path = out if out.endswith(extension) else out + extension
            with open(path, "w") as of:
                cls.print_to_stream(mdl, of)
                # print("* file: %s overwritten" % path)
        else:
            try:
                cls.print(out, mdl)

            except AttributeError:  # pragma: no cover
                pass  # pragma: no cover
                # stringio will raise an attribute error here, due to with
                # print("Cannot use this an output: %s" % str(out))

    @classmethod
    def print_to_string(cls, mdl):
        oss = StringIO()
        cls.print_to_stream(mdl, out=oss)
        return oss.getvalue()
