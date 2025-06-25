

def get_start(graph):
    start_node = get_node_by_type("start", graph)
    return get_next_node_by_source_id(start_node["id"], graph)


def get_next_node_by_source_id(source_id, graph):
    id = get_next_node_id_by_source_id(source_id, graph)
    return get_node_by_id(id, graph)


def get_next_node_id_by_source_id(source_id, graph, for_btn: bool = False, condition_value: bool=None):
    if for_btn:
        edge = next((edge for edge in graph["edges"] if edge["sourceHandle"] == 'btn-' + source_id), None)
    else:
        if condition_value is not None:
            if condition_value:
                edge = next((edge for edge in graph["edges"] if
                         edge["source"] == source_id and edge["sourceHandle"] == "true"), None)
            else:
                edge = next((edge for edge in graph["edges"] if
                             edge["source"] == source_id and edge[
                                 "sourceHandle"] == "false"), None)
        else:
            edge = next((edge for edge in graph["edges"] if edge["source"] == source_id), None)
    return edge and edge["target"]


def get_node_by_id(id, graph):
    return next((node for node in graph["nodes"] if node["id"] == id), None)


def get_node_by_type(type, graph):
    return next((node for node in graph["nodes"] if node["type"] == type), None)
