#!/usr/bin/env python3
"""
BPMN Diff Filter
Removes diagram interchange data and normalises metadata to produce cleaner diffs
"""
import sys
import xml.etree.ElementTree as ET


def filter_bpmn(input_stream):
    """
    Filter BPMN XML to show only meaningful changes:
    1. Remove entire BPMNDiagram section (visual layout)
    2. Normalise exporter version (changes with Modeler updates)
    3. Remove color/bioc namespaces (styling)
    """
    try:
        # Parse the XML
        tree = ET.parse(input_stream)
        root = tree.getroot()

        # Define namespaces
        namespaces = {
            'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
            'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
            'dc': 'http://www.omg.org/spec/DD/20100524/DC',
            'di': 'http://www.omg.org/spec/DD/20100524/DI',
            'camunda': 'http://camunda.org/schema/1.0/bpmn',
            'modeler': 'http://camunda.org/schema/modeler/1.0',
            'bioc': 'http://bpmn.io/schema/bpmn/biocolor/1.0',
            'color': 'http://www.omg.org/spec/BPMN/non-normative/color/1.0'
        }

        # Register namespaces to preserve prefixes
        for prefix, uri in namespaces.items():
            ET.register_namespace(prefix, uri)

        # Remove BPMNDiagram elements (all visual layout data)
        for diagram in root.findall('.//bpmndi:BPMNDiagram', namespaces):
            root.remove(diagram)

        # Normalise exporter version (changes with Modeler updates)
        if 'exporterVersion' in root.attrib:
            root.attrib['exporterVersion'] = 'X.XX.X'

        # Remove color/styling namespace declarations from root
        attribs_to_remove = []
        for attr in root.attrib:
            if 'bioc' in attr or 'color' in attr:
                attribs_to_remove.append(attr)
        for attr in attribs_to_remove:
            del root.attrib[attr]

        # Write formatted XML to stdout
        ET.indent(tree, space='  ')
        tree.write(sys.stdout.buffer, encoding='utf-8', xml_declaration=True)

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Called by git textconv with filename as argument
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            filter_bpmn(f)
    else:
        # Called directly with stdin
        filter_bpmn(sys.stdin)