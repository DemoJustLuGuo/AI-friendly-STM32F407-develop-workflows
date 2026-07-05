# Software Integration Notes

Use the script as a portable CLI, or lift its functions into an application module.

Recommended backend shape:

- `SchematicReader.summary(project_path)`
- `SchematicReader.components(project_path, filters)`
- `SchematicReader.nets(project_path, filters)`
- `SchematicReader.connections(project_path, designator, pin=None)`
- `SchematicReader.bom(project_path, variant=None)`
- `SchematicReader.sheet(schdoc_path)`

Recommended API endpoints:

- `GET /projects/{project_id}/summary`
- `GET /projects/{project_id}/components`
- `GET /projects/{project_id}/components/{designator}`
- `GET /projects/{project_id}/nets`
- `GET /projects/{project_id}/nets/{net_name}`
- `GET /projects/{project_id}/connections/{designator}`
- `GET /projects/{project_id}/connections/{designator}/{pin}`
- `GET /projects/{project_id}/bom`
- `POST /projects/{project_id}/ask`

Store two kinds of artifacts:

- Raw artifacts: full design JSON, full netlist JSON, optional SVG renders.
- Query cache: summary, component slices, net terminal lists, BOM items, AI evidence.

AI workflow:

1. Load project summary.
2. Select relevant sheets, components, or nets.
3. Query targeted JSON slices.
4. Answer with evidence: designator, pin, net, sheet, BOM line.
5. Mark uncertain interpretation as hypothesis, not fact.
