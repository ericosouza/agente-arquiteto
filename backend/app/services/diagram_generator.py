"""Gerador de Diagramas ArchiMate (Etapa 6).

Gera diagramas SVG de alta fidelidade em conformidade com a notação visual do ArchiMate 3.2:
- Agrupamento em faixas de camadas oficiais (Channel, Business, Application, Technology).
- Paletas de cores oficiais do padrão ArchiMate:
    * Channel: Âmbar / Dourado (#FEF3C7 / #D97706)
    * Business: Amarelo suave (#FFF9C4 / #FBC02D)
    * Application: Azul ciano claro (#E1F5FE / #0288D1)
    * Technology: Verde suave (#E8F5E9 / #388E3C)
- Glifos visuais dos tipos de elementos no canto superior direito:
    * Application Component (retângulo com abas salientes à esquerda)
    * Application Service (cápsula / pílula arredondada)
    * Data Object (documento com canto dobrado)
    * System Software / Node (cubo 3D ou cilindro de banco de dados)
    * Business Actor (ícone de ator)
- Pontas de flechas padronizadas para relacionamentos (Serving, Access, Realization, Assignment, Flow).
- Layout organizado em camadas evitando sobreposição de nós.
"""

from typing import Dict, List, Tuple
from app.models.archimate import (
    ArchiMateModel,
    ArchiMateElement,
    ArchiMateRelationship,
    ArchiMateLayer,
    ArchiMateElementType,
    ArchiMateRelationshipType,
    ArchiMateView,
    ArchiMateViewNode,
    ArchiMateViewConnection,
    LAYER_COLORS,
)


class DiagramGenerator:
    """Gera diagramas ArchiMate em SVG e calcula as coordenadas de layout na visualização do modelo."""

    NODE_WIDTH = 290
    NODE_HEIGHT = 104
    HORIZONTAL_GAP = 45
    VERTICAL_LAYER_GAP = 120
    PADDING = 50

    @classmethod
    def layout_and_render_svg(cls, model: ArchiMateModel) -> Tuple[str, ArchiMateModel]:
        """Calcula o layout de todos os elementos, atualiza os nós da visão do modelo e renderiza o SVG completo."""
        # 1. Agrupa os elementos por camada
        channel_elems = [e for e in model.elements if e.layer == ArchiMateLayer.CHANNEL]
        business_elems = [e for e in model.elements if e.layer == ArchiMateLayer.BUSINESS]
        app_elems = [e for e in model.elements if e.layer == ArchiMateLayer.APPLICATION]
        tech_elems = [e for e in model.elements if e.layer == ArchiMateLayer.TECHNOLOGY]
        other_elems = [e for e in model.elements if e.layer not in {
            ArchiMateLayer.CHANNEL, ArchiMateLayer.BUSINESS, ArchiMateLayer.APPLICATION, ArchiMateLayer.TECHNOLOGY
        }]

        layers_ordered = [
            ("Channel Layer", ArchiMateLayer.CHANNEL, channel_elems),
            ("Business Layer", ArchiMateLayer.BUSINESS, business_elems),
            ("Application Layer", ArchiMateLayer.APPLICATION, app_elems),
            ("Technology Layer", ArchiMateLayer.TECHNOLOGY, tech_elems),
        ]
        if other_elems:
            layers_ordered.append(("Outros Elementos", ArchiMateLayer.PHYSICAL, other_elems))

        # Filtra camadas completamente vazias (sem elementos)
        active_layers = [(title, layer, elems) for title, layer, elems in layers_ordered if len(elems) > 0]
        if not active_layers:
            # Fallback se não houver camadas ativas
            active_layers = [("Application Layer", ArchiMateLayer.APPLICATION, model.elements)]

        # Determina a largura do canvas com base no número máximo de itens em uma única camada
        max_items_in_layer = max((len(elems) for _, _, elems in active_layers), default=1)
        # Limita a linha a no máximo 4 itens; quebra para a próxima linha se houver mais
        max_cols = min(max(max_items_in_layer, 2), 4)

        band_content_width = max_cols * cls.NODE_WIDTH + (max_cols - 1) * cls.HORIZONTAL_GAP
        canvas_width = max(band_content_width + cls.PADDING * 2 + 100, 1000)

        # 2. Posicionamento dos elementos
        current_y = cls.PADDING + 40
        node_positions: Dict[str, Dict[str, float]] = {}
        layer_bands: List[Dict[str, any]] = []
        view_nodes: List[ArchiMateViewNode] = []

        for layer_title, layer_enum, elems in active_layers:
            start_y = current_y
            rows_count = (len(elems) + max_cols - 1) // max_cols if elems else 1

            # Centraliza os elementos horizontalmente no canvas
            for idx, elem in enumerate(elems):
                row = idx // max_cols
                col = idx % max_cols

                items_in_this_row = min(len(elems) - row * max_cols, max_cols)
                row_width = items_in_this_row * cls.NODE_WIDTH + (items_in_this_row - 1) * cls.HORIZONTAL_GAP
                offset_x = (canvas_width - row_width) / 2

                pos_x = offset_x + col * (cls.NODE_WIDTH + cls.HORIZONTAL_GAP)
                pos_y = start_y + 40 + row * (cls.NODE_HEIGHT + 40)

                node_positions[elem.id] = {
                    "x": pos_x,
                    "y": pos_y,
                    "width": cls.NODE_WIDTH,
                    "height": cls.NODE_HEIGHT,
                    "elem": elem,
                }
                view_nodes.append(ArchiMateViewNode(
                    elementId=elem.id,
                    x=pos_x,
                    y=pos_y,
                    width=cls.NODE_WIDTH,
                    height=cls.NODE_HEIGHT,
                ))

            band_height = 50 + rows_count * (cls.NODE_HEIGHT + 40)
            layer_bands.append({
                "title": layer_title,
                "layer": layer_enum,
                "x": cls.PADDING,
                "y": start_y,
                "width": canvas_width - cls.PADDING * 2,
                "height": band_height,
            })
            current_y += band_height + cls.VERTICAL_LAYER_GAP

        canvas_height = current_y + cls.PADDING

        # 3. Criação das conexões da visão
        view_connections: List[ArchiMateViewConnection] = []
        for rel in model.relationships:
            if rel.source in node_positions and rel.target in node_positions:
                view_connections.append(ArchiMateViewConnection(
                    relationshipId=rel.id,
                    sourceId=rel.source,
                    targetId=rel.target,
                ))

        # Atualiza a visualização padrão do modelo
        model.views = [ArchiMateView(
            id="view-main",
            name="Visão Geral da Arquitetura ArchiMate",
            documentation="Diagrama gerado automaticamente pelo AI Architecture Designer",
            nodes=view_nodes,
            connections=view_connections,
        )]

        # 4. Renderização do SVG
        svg = cls._render_svg_markup(
            canvas_width, canvas_height, layer_bands, node_positions, model.relationships, model.name
        )
        return svg, model

    @classmethod
    def _render_svg_markup(
        cls,
        width: float,
        height: float,
        layer_bands: List[Dict[str, any]],
        node_positions: Dict[str, Dict[str, any]],
        relationships: List[ArchiMateRelationship],
        model_name: str,
    ) -> str:
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" '
            f'style="background-color: #F8FAFC; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">',
            cls._render_defs(),
        ]

        # Padrão de grade de fundo
        svg_parts.append(f'<rect width="{width}" height="{height}" fill="url(#grid)" />')

        # Cabeçalho e Título do Diagrama
        svg_parts.append(f'''
        <g id="diagram-header" transform="translate({cls.PADDING}, 35)">
            <text x="0" y="0" font-size="20" font-weight="700" fill="#0F172A">{model_name}</text>
            <text x="0" y="20" font-size="12" fill="#64748B">Notação Oficial ArchiMate 3.2 • Gerado por AI Software Architecture Designer</text>
        </g>
        ''')

        # Faixas de contêineres de camadas
        for band in layer_bands:
            layer_info = LAYER_COLORS.get(band["layer"], LAYER_COLORS[ArchiMateLayer.APPLICATION])
            svg_parts.append(f'''
            <g id="layer-band-{band['title'].replace(' ', '_')}">
                <!-- Caixa Contêiner da Camada -->
                <rect x="{band['x']}" y="{band['y']}" width="{band['width']}" height="{band['height']}"
                      rx="12" ry="12" fill="{layer_info['fill']}" fill-opacity="0.25"
                      stroke="{layer_info['stroke']}" stroke-width="1.5" stroke-dasharray="6,4" />
                <!-- Banner de Identificação da Camada -->
                <rect x="{band['x'] + 16}" y="{band['y'] - 14}" width="{len(band['title']) * 9 + 30}" height="26"
                      rx="6" ry="6" fill="{layer_info['stroke']}" />
                <text x="{band['x'] + 26}" y="{band['y'] + 4}" font-size="12" font-weight="700" fill="#FFFFFF">{band['title']}</text>
            </g>
            ''')

        # Relacionamentos (linhas renderizadas antes dos nós para ficarem atrás das caixas)
        for rel in relationships:
            if rel.source in node_positions and rel.target in node_positions:
                src_pos = node_positions[rel.source]
                tgt_pos = node_positions[rel.target]
                svg_parts.append(cls._render_relationship(rel, src_pos, tgt_pos))

        # Elementos (nós do diagrama)
        for elem_id, pos in node_positions.items():
            svg_parts.append(cls._render_element_node(pos))

        svg_parts.append('</svg>')
        return "\n".join(svg_parts)

    @classmethod
    def _render_defs(cls) -> str:
        """Define marcadores, setas, glifos e filtros para a notação visual ArchiMate."""
        return '''
        <defs>
            <!-- Grade de Fundo -->
            <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#E2E8F0" stroke-width="0.8" opacity="0.6"/>
            </pattern>

            <!-- Filtro de Sombra Suave -->
            <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
                <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#0F172A" flood-opacity="0.08" />
            </filter>

            <!-- Marcadores de Relacionamento ArchiMate -->
            <!-- Serving: Flecha Aberta -->
            <marker id="marker-serving" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 1 L 9 5 L 0 9" fill="none" stroke="#334155" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            </marker>

            <!-- Access: Flecha Aberta com convenção de linha tracejada -->
            <marker id="marker-access" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 1 L 9 5 L 0 9" fill="none" stroke="#0284C7" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            </marker>

            <!-- Realization: Flecha Triangular Vazada -->
            <marker id="marker-realization" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="9" markerHeight="9" orient="auto-start-reverse">
                <path d="M 0 1 L 11 6 L 0 11 Z" fill="#FFFFFF" stroke="#334155" stroke-width="1.6" stroke-linejoin="round" />
            </marker>

            <!-- Assignment: Círculo Preenchido -->
            <marker id="marker-assignment" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <circle cx="5" cy="5" r="4" fill="#334155" />
            </marker>

            <!-- Flow: Flecha com Cabeça Sólida Preenchida -->
            <marker id="marker-flow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 1 L 9 5 L 0 9 Z" fill="#334155" />
            </marker>

            <!-- Association: Linha simples padrão (sem cabeça de seta) -->
        </defs>
        '''

    @classmethod
    def _render_element_node(cls, pos: Dict[str, any]) -> str:
        elem: ArchiMateElement = pos["elem"]
        x, y, w, h = pos["x"], pos["y"], pos["width"], pos["height"]
        layer_color = LAYER_COLORS.get(elem.layer, LAYER_COLORS[ArchiMateLayer.APPLICATION])

        tech = elem.properties.get("technology", "")
        resp = elem.documentation or elem.properties.get("responsibility", "")

        # Trunca o texto para caber nas caixas de nós (suporta nomes padronizados como sboot-sesg-base-atom-risco-ambiental)
        name_clean = elem.name[:44] + ("..." if len(elem.name) > 44 else "")
        tech_clean = tech[:38] + ("..." if len(tech) > 38 else "")
        resp_clean = resp[:46] + ("..." if len(resp) > 46 else "")

        glyph_svg = cls._render_element_glyph(elem.type, x + w - 30, y + 8)

        return f'''
        <g id="element-{elem.id}" filter="url(#shadow)">
            <!-- Contêiner Principal do Card -->
            <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" ry="8"
                  fill="{layer_color['fill']}" stroke="{layer_color['stroke']}" stroke-width="1.8" />

            <!-- Cabeçalho do Card com Destaque de Cor -->
            <rect x="{x}" y="{y}" width="{w}" height="28" rx="8" ry="8"
                  fill="{layer_color['header']}" />
            <rect x="{x}" y="{y + 20}" width="{w}" height="8"
                  fill="{layer_color['header']}" />

            <!-- Glifo Oficial do Tipo ArchiMate -->
            {glyph_svg}

            <!-- Subtítulo com o Tipo do Elemento -->
            <text x="{x + 10}" y="{y + 18}" font-size="9" font-weight="700" fill="{layer_color['stroke']}" letter-spacing="0.5">
                {elem.type.value.upper()}
            </text>

            <!-- Nome do Elemento -->
            <text x="{x + 10}" y="{y + 44}" font-size="11" font-weight="700" fill="#0F172A">
                {name_clean}
            </text>

            <!-- Tag de Tecnologia -->
            {f"""<rect x="{x + 10}" y="{y + 54}" width="{min(len(tech_clean)*6 + 14, w - 20)}" height="16" rx="4" fill="#FFFFFF" fill-opacity="0.85" stroke="{layer_color['stroke']}" stroke-width="0.8"/>
            <text x="{x + 16}" y="{y + 66}" font-size="9.5" font-weight="600" fill="{layer_color['stroke']}">
                ⚙ {tech_clean}
            </text>""" if tech else ""}

            <!-- Resumo da Responsabilidade Arquitetural -->
            <text x="{x + 10}" y="{y + 88}" font-size="9.5" fill="#475569" font-style="italic">
                {resp_clean}
            </text>
        </g>
        '''

    @classmethod
    def _render_element_glyph(cls, elem_type: ArchiMateElementType, gx: float, gy: float) -> str:
        """Renderiza o símbolo oficial ArchiMate no canto superior direito do nó."""
        if elem_type == ArchiMateElementType.APPLICATION_COMPONENT:
            # Component: retângulo com duas abas pequenas na esquerda
            return f'''
            <g transform="translate({gx}, {gy})">
                <rect x="5" y="2" width="16" height="14" fill="none" stroke="#0288D1" stroke-width="1.4" rx="1"/>
                <rect x="2" y="4" width="6" height="3" fill="#FFFFFF" stroke="#0288D1" stroke-width="1.2"/>
                <rect x="2" y="10" width="6" height="3" fill="#FFFFFF" stroke="#0288D1" stroke-width="1.2"/>
            </g>
            '''
        elif elem_type == ArchiMateElementType.APPLICATION_SERVICE or elem_type == ArchiMateElementType.TECHNOLOGY_SERVICE:
            # Service: cápsula arredondada
            stroke_color = "#388E3C" if elem_type == ArchiMateElementType.TECHNOLOGY_SERVICE else "#0288D1"
            return f'''
            <g transform="translate({gx}, {gy})">
                <rect x="2" y="4" width="20" height="10" rx="5" ry="5" fill="none" stroke="{stroke_color}" stroke-width="1.4"/>
            </g>
            '''
        elif elem_type == ArchiMateElementType.DATA_OBJECT:
            # Data Object: documento com dobra no canto
            return f'''
            <g transform="translate({gx + 4}, {gy})">
                <path d="M 0 0 L 10 0 L 15 5 L 15 16 L 0 16 Z" fill="none" stroke="#0288D1" stroke-width="1.4" />
                <path d="M 10 0 L 10 5 L 15 5" fill="none" stroke="#0288D1" stroke-width="1.4" />
            </g>
            '''
        elif elem_type in {ArchiMateElementType.NODE, ArchiMateElementType.DEVICE}:
            # Node: cubo isométrico 3D
            return f'''
            <g transform="translate({gx}, {gy})">
                <polygon points="4,5 12,2 20,5 12,8" fill="none" stroke="#388E3C" stroke-width="1.3" />
                <polygon points="4,5 12,8 12,16 4,13" fill="none" stroke="#388E3C" stroke-width="1.3" />
                <polygon points="20,5 12,8 12,16 20,13" fill="none" stroke="#388E3C" stroke-width="1.3" />
            </g>
            '''
        elif elem_type == ArchiMateElementType.SYSTEM_SOFTWARE:
            # System Software: cilindro de banco de dados ou discos empilhados
            return f'''
            <g transform="translate({gx + 2}, {gy + 1})">
                <ellipse cx="9" cy="4" rx="8" ry="2.5" fill="none" stroke="#388E3C" stroke-width="1.3"/>
                <path d="M 1 4 L 1 12 A 8 2.5 0 0 0 17 12 L 17 4" fill="none" stroke="#388E3C" stroke-width="1.3"/>
                <ellipse cx="9" cy="8" rx="8" ry="2" fill="none" stroke="#388E3C" stroke-width="0.9" stroke-dasharray="2,2"/>
            </g>
            '''
        elif elem_type == ArchiMateElementType.BUSINESS_ACTOR:
            # Actor: silhueta de pessoa
            return f'''
            <g transform="translate({gx + 4}, {gy})">
                <circle cx="8" cy="4" r="3" fill="none" stroke="#F57F17" stroke-width="1.4"/>
                <path d="M 8 7 L 8 13 M 4 9 L 12 9 M 5 16 L 8 13 L 11 16" fill="none" stroke="#F57F17" stroke-width="1.4" stroke-linecap="round"/>
            </g>
            '''
        else:
            # Caixa genérica
            return f'''
            <g transform="translate({gx + 4}, {gy})">
                <rect x="0" y="2" width="16" height="12" fill="none" stroke="#64748B" stroke-width="1.3" rx="2"/>
            </g>
            '''

    @classmethod
    def _render_relationship(
        cls,
        rel: ArchiMateRelationship,
        src: Dict[str, any],
        tgt: Dict[str, any]
    ) -> str:
        """Desenha conexão ortogonal ou curvada entre os nós de origem e destino com marcadores visuais."""
        src_cx = src["x"] + src["width"] / 2
        src_cy = src["y"] + src["height"] / 2
        tgt_cx = tgt["x"] + tgt["width"] / 2
        tgt_cy = tgt["y"] + tgt["height"] / 2

        # Determina os pontos de saída e entrada
        if abs(tgt_cy - src_cy) > abs(tgt_cx - src_cx):
            # Conexão vertical predominante
            if tgt_cy > src_cy:
                # Descendente
                p1_x, p1_y = src_cx, src["y"] + src["height"]
                p2_x, p2_y = tgt_cx, tgt["y"]
            else:
                # Ascendente
                p1_x, p1_y = src_cx, src["y"]
                p2_x, p2_y = tgt_cx, tgt["y"] + tgt["height"]
        else:
            # Conexão horizontal predominante
            if tgt_cx > src_cx:
                # Direita
                p1_x, p1_y = src["x"] + src["width"], src_cy
                p2_x, p2_y = tgt["x"], tgt_cy
            else:
                # Esquerda
                p1_x, p1_y = src["x"], src_cy
                p2_x, p2_y = tgt["x"] + tgt["width"], tgt_cy

        # Ponto médio para o rótulo
        mid_x = (p1_x + p2_x) / 2
        mid_y = (p1_y + p2_y) / 2

        # Estilo de acordo com o tipo de relacionamento ArchiMate
        stroke_color = "#334155"
        stroke_width = "1.6"
        stroke_dash = "none"
        marker_end = "url(#marker-serving)"

        if rel.type == ArchiMateRelationshipType.ACCESS:
            stroke_color = "#0284C7"
            stroke_dash = "5,4"
            marker_end = "url(#marker-access)"
        elif rel.type == ArchiMateRelationshipType.SERVING:
            stroke_color = "#334155"
            stroke_dash = "none"
            marker_end = "url(#marker-serving)"
        elif rel.type == ArchiMateRelationshipType.REALIZATION:
            stroke_color = "#475569"
            stroke_dash = "6,4"
            marker_end = "url(#marker-realization)"
        elif rel.type == ArchiMateRelationshipType.ASSIGNMENT:
            stroke_color = "#1E293B"
            stroke_dash = "none"
            marker_end = "url(#marker-assignment)"
        elif rel.type == ArchiMateRelationshipType.FLOW:
            stroke_color = "#334155"
            stroke_dash = "4,3"
            marker_end = "url(#marker-flow)"
        elif rel.type == ArchiMateRelationshipType.ASSOCIATION:
            stroke_color = "#64748B"
            stroke_dash = "none"
            marker_end = "none"

        # Traçado suave de curva Bézier cúbica
        ctrl1_y = p1_y + (p2_y - p1_y) * 0.5
        ctrl2_y = p1_y + (p2_y - p1_y) * 0.5
        path_d = f"M {p1_x} {p1_y} C {p1_x} {ctrl1_y}, {p2_x} {ctrl2_y}, {p2_x} {p2_y}"

        # Extrai metadados do rótulo (protocolo e finalidade)
        protocol = rel.properties.get("protocol", "")
        pattern = rel.properties.get("communicationPattern", "")
        label_text = rel.name or protocol or rel.type.value
        if pattern and pattern.lower() == "asynchronous":
            label_text += " (Async)"

        label_width = len(label_text) * 6 + 14

        return f'''
        <g id="relation-{rel.id}">
            <!-- Traçado da Linha -->
            <path d="{path_d}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_width}"
                  stroke-dasharray="{stroke_dash}" marker-end="{marker_end}" opacity="0.85" />

            <!-- Pílula do Rótulo de Integração -->
            <g transform="translate({mid_x - label_width / 2}, {mid_y - 10})">
                <rect x="0" y="0" width="{label_width}" height="18" rx="9" ry="9"
                      fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1" />
                <text x="{label_width / 2}" y="12" font-size="9" font-weight="600" fill="#475569" text-anchor="middle">
                    {label_text}
                </text>
            </g>
        </g>
        '''
