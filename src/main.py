import argparse
import json
from .graph import get_app


def main():
    parser = argparse.ArgumentParser(description='Triagem de suporte: somente dados fictícios.')
    sub = parser.add_subparsers(dest='comando', required=True)
    start = sub.add_parser('iniciar')
    start.add_argument('texto', nargs='?')
    start.add_argument('--usuario', default='demo')
    start.add_argument('--sessao', default='principal')
    start.add_argument('--caso', default='caso1')
    resume = sub.add_parser('retomar')
    resume.add_argument('thread')
    resume.add_argument('decisao', choices=['aprovar', 'rejeitar', 'editar'])
    resume.add_argument('--prioridade', choices=['Baixa', 'Média', 'Alta', 'Crítica'])
    resume.add_argument('--equipe', choices=['Suporte N1', 'Infraestrutura', 'Sistemas', 'Suporte N2'])
    sub.add_parser('expirar')
    forget = sub.add_parser('esquecer')
    forget.add_argument('usuario')
    args = parser.parse_args()
    app = get_app()
    try:
        if args.comando == 'iniciar':
            result = app.run(args.texto or input('Descreva o problema: '), args.usuario, args.sessao, args.caso)
        elif args.comando == 'retomar':
            result = app.resume(args.thread, {'decisao': args.decisao, 'prioridade': args.prioridade, 'encaminhamento': args.equipe})
        elif args.comando == 'expirar':
            result = app.expire()
        else:
            result = app.store.forget(args.usuario, app.checkpointer)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
