"""ArchiMate Model Exporters (Etapa 7).

Provides structured export in:
1. Standard ArchiMate 3.2 JSON format.
2. The Open Group ArchiMate Model Exchange File Format (XML / .archimate).
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Any
from app.models.archimate import ArchiMateModel


class ArchiMateExporter:
    """Exports ArchiMate models into structured JSON and standard Open Group XML."""

    @classmethod
    def to_json_dict(cls, model: ArchiMateModel) -> Dict[str, Any]:
        """Converts model to structured ArchiMate 3.2 JSON format."""
        return {
            "$schema": "https://www.opengroup.org/archimate/3.2/model.json",
            "identifier": model.identifier,
            "name": model.name,
            "documentation": model.documentation,
            "version": model.version,
            "metadata": {
                "author": model.metadata.author,
                "createdAt": model.metadata.createdAt,
                "standard": model.metadata.standard,
                "description": model.metadata.description,
                "architecturalStyle": model.metadata.architecturalStyle,
            },
            "elements": [
                {
                    "identifier": elem.id,
                    "name": elem.name,
                    "type": elem.type.value,
                    "layer": elem.layer.value,
                    "documentation": elem.documentation,
                    "properties": elem.properties,
                }
                for elem in model.elements
            ],
            "relationships": [
                {
                    "identifier": rel.id,
                    "name": rel.name or "",
                    "type": rel.type.value,
                    "source": rel.source,
                    "target": rel.target,
                    "documentation": rel.documentation or "",
                    "properties": rel.properties,
                }
                for rel in model.relationships
            ],
            "views": [
                {
                    "identifier": view.id,
                    "name": view.name,
                    "documentation": view.documentation or "",
                    "nodes": [
                        {
                            "elementRef": n.elementId,
                            "x": n.x,
                            "y": n.y,
                            "width": n.width,
                            "height": n.height,
                        }
                        for n in view.nodes
                    ],
                    "connections": [
                        {
                            "relationshipRef": c.relationshipId,
                            "sourceRef": c.sourceId,
                            "targetRef": c.targetId,
                        }
                        for c in view.connections
                    ],
                }
                for view in model.views
            ],
        }

    @classmethod
    def to_json_string(cls, model: ArchiMateModel) -> str:
        """Serializes the ArchiMate model to formatted JSON."""
        data = cls.to_json_dict(model)
        return json.dumps(data, indent=2, ensure_ascii=False)

    @classmethod
    def to_opengroup_xml(cls, model: ArchiMateModel) -> str:
        """Exports the model to The Open Group ArchiMate Model Exchange Format (3.0/3.2 XML).

        This format is fully compatible with Archi and other enterprise architecture tools.
        """
        ns_uri = "http://www.opengroup.org/xsd/archimate/3.0/"
        xsi_uri = "http://www.w3.org/2001/XMLSchema-instance"

        # Root element: <model>
        root = ET.Element(
            "model",
            {
                "xmlns": ns_uri,
                "xmlns:xsi": xsi_uri,
                "identifier": model.identifier,
                "xsi:schemaLocation": f"{ns_uri} http://www.opengroup.org/xsd/archimate/3.0/archimate3_Diagram.xsd",
            },
        )

        # Name & Documentation
        name_elem = ET.SubElement(root, "name")
        name_elem.text = model.name
        name_elem.set("xml:lang", "pt")

        doc_elem = ET.SubElement(root, "documentation")
        doc_elem.text = model.documentation
        doc_elem.set("xml:lang", "pt")

        # Elements container
        elements_container = ET.SubElement(root, "elements")
        for elem in model.elements:
            el = ET.SubElement(
                elements_container,
                "element",
                {
                    "identifier": elem.id,
                    "xsi:type": elem.type.value,
                },
            )
            el_name = ET.SubElement(el, "name")
            el_name.text = elem.name
            el_name.set("xml:lang", "pt")

            if elem.documentation:
                el_doc = ET.SubElement(el, "documentation")
                el_doc.text = elem.documentation
                el_doc.set("xml:lang", "pt")

            if elem.properties:
                props_container = ET.SubElement(el, "properties")
                for k, v in elem.properties.items():
                    prop = ET.SubElement(props_container, "property")
                    prop_key = ET.SubElement(prop, "key")
                    prop_key.text = k
                    prop_val = ET.SubElement(prop, "value")
                    prop_val.text = str(v)

        # Relationships container
        relationships_container = ET.SubElement(root, "relationships")
        for rel in model.relationships:
            r = ET.SubElement(
                relationships_container,
                "relationship",
                {
                    "identifier": rel.id,
                    "source": rel.source,
                    "target": rel.target,
                    "xsi:type": rel.type.value,
                },
            )
            if rel.name:
                r_name = ET.SubElement(r, "name")
                r_name.text = rel.name
                r_name.set("xml:lang", "pt")
            if rel.documentation:
                r_doc = ET.SubElement(r, "documentation")
                r_doc.text = rel.documentation
                r_doc.set("xml:lang", "pt")

        # Views container
        if model.views:
            views_container = ET.SubElement(root, "views")
            diagrams_container = ET.SubElement(views_container, "diagrams")
            for view in model.views:
                v = ET.SubElement(
                    diagrams_container,
                    "view",
                    {
                        "identifier": view.id,
                        "xsi:type": "Diagram",
                    },
                )
                v_name = ET.SubElement(v, "name")
                v_name.text = view.name
                for node in view.nodes:
                    ET.SubElement(
                        v,
                        "node",
                        {
                            "elementRef": node.elementId,
                            "x": str(int(node.x)),
                            "y": str(int(node.y)),
                            "w": str(int(node.width)),
                            "h": str(int(node.height)),
                        },
                    )

        ET.indent(root, space="  ")
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        return xml_declaration + ET.tostring(root, encoding="unicode")
