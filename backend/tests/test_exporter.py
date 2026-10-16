"""Tests for ArchiMate Exporter service (JSON and Open Group XML)."""

import json
import xml.etree.ElementTree as ET
import pytest
from app.services.architect_agent import ArchitectAgent
from app.services.exporter import ArchiMateExporter


@pytest.mark.asyncio
async def test_export_json_and_xml_consistency():
    description = "Sistema de produtos simples"
    proposal = await ArchitectAgent.analyze_and_propose(description)
    model, _, _ = ArchitectAgent.generate_archimate_model_from_proposal(proposal)

    # 1. Test JSON Export
    json_str = ArchiMateExporter.to_json_string(model)
    json_data = json.loads(json_str)

    assert json_data["version"] == "3.2"
    assert json_data["identifier"] == model.identifier
    assert len(json_data["elements"]) == len(model.elements)
    assert len(json_data["relationships"]) == len(model.relationships)

    # Check that element types and IDs are present
    for elem_dict in json_data["elements"]:
        assert "identifier" in elem_dict
        assert "type" in elem_dict
        assert "layer" in elem_dict

    # 2. Test Open Group XML Export
    xml_str = ArchiMateExporter.to_opengroup_xml(model)
    assert xml_str.startswith('<?xml version="1.0" encoding="UTF-8"?>')

    # Parse XML to verify valid XML syntax
    root = ET.fromstring(xml_str.replace('<?xml version="1.0" encoding="UTF-8"?>', '').strip())
    assert "model" in root.tag
    assert root.attrib.get("identifier") == model.identifier

    # Check elements and relationships containers
    elements_xml = root.find("{http://www.opengroup.org/xsd/archimate/3.0/}elements")
    assert elements_xml is not None
    assert len(elements_xml) == len(model.elements)
