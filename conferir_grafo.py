"""Inspeciona o mesmo objeto compilado usado pela CLI."""
from src.graph import get_app


def inventory():
    graph = get_app().graph.get_graph()
    return '\n'.join(['NÓS', *sorted(graph.nodes), 'ARESTAS',
                      *sorted(f'{e.source} -> {e.target}' + (' [condicional]' if e.conditional else '') for e in graph.edges)])


if __name__ == '__main__':
    print(inventory())
