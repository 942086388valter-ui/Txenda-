# TXENDA — Sistema Inteligente de Gestão Escolar (V3)

## Funcionalidades incluídas
- Autenticação e perfis administrativos, docentes e estudantes.
- Gestão de estudantes, professores, turmas, disciplinas e matrículas.
- Registo de notas, presenças e faltas justificadas.
- Configuração do nome, sigla, contactos, endereço e logótipo da instituição.
- Emissão de boletins de notas e certificados de matrícula em PDF.
- Relatório global de desempenho em PDF (administrador).
- Registo de auditoria das emissões de documentos e alterações institucionais.
- Base de dados SQLite para instalação local.

## Instalação no Windows
Instale Python 3.10 ou superior. Abra PowerShell dentro da pasta TXENDA:
1. `py -m venv .venv`
2. `.venv\\Scripts\\activate`
3. `pip install -r requirements.txt`
4. `python manage.py makemigrations school`
5. `python manage.py migrate`
6. `python manage.py createsuperuser`
7. `python manage.py runserver`
Abra `http://127.0.0.1:8000/`.

## Configuração institucional
Entre com a conta de administrador e abra **Instituição**. Preencha os dados e carregue o logótipo. Esses dados serão impressos nos documentos PDF.

## Segurança e limites desta versão
Esta é uma versão de desenvolvimento/MVP. Antes de utilização real, configure uma chave secreta forte, `DEBUG=False`, `ALLOWED_HOSTS`, HTTPS, backups externos e política de privacidade. Faça testes com dados fictícios antes de inserir dados reais. O modo offline com sincronização automática, aplicação Android/Windows nativa e isolamento de várias instituições ainda não estão implementados nesta versão.


## PWA e suporte básico a ligação intermitente (V4)
- O TXENDA pode ser instalado como aplicação web progressiva (PWA) em navegadores compatíveis.
- Guarda a página de contingência e recursos estáticos em cache.
- Se um formulário for submetido sem rede, o pedido POST é colocado numa fila local do navegador e tenta ser reenviado quando a ligação regressar.
- Para sincronizar, mantenha o navegador com os dados do site e volte a iniciar sessão se a sessão tiver expirado.

**Limitações importantes:** isto é uma camada inicial de contingência, não uma sincronização offline completa de toda a base de dados. Páginas privadas e dados escolares não são guardados em cache. O reenvio depende da sessão, do suporte do navegador à Background Sync e da validade do formulário/CSRF. Antes de uso real, devem ser criados endpoints de sincronização idempotentes, confirmação visual de pedidos pendentes e testes em Android/Windows. Não utilize o modo de contingência como única cópia de dados.
