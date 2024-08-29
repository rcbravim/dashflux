## ROADMAP

### Prioridade 0
    - bug: edit contas não está funcionando bem
    - enh: adicionar todas as informações em backup, descrições, categorias, etc
    - bug: ao restaurar backup e importar CSV, esetabelecimentos (e possivelmente categoria e contas) com nome padrão do sistema, criam-se novos cadastros

### Prioridade 1
    - bug: ao editar despesa, não é possível colocar mais de uma categoria
    - bug: editar despesa no celular, teclado sumindo e aparecendo repetidamente
    - enh: não cadastrar nada que seja string como NULL no banco, mas sim como "" (vazio)

### Prioridade 2
    - enh: ajustar responsividade para celular de todas paginas e funções
    - enh: alterar o botão de add transação para um botão flutuante
    - enh: módulo sesssões de login (logs)
    - resolver questão de espaço física (logs em filesystem?)
    - enh: adicionar csv nas transações, como em fatura de cartão

### Prioridade 3
    - criar rotina deploy que contenha alteração de banco de dados


### Done
    - bug: Categorias invertidas ou durante inserçao do CSV ou restaurar backup
    - enh: acrescentar descrição para categoria
    - enh: acrescentar metas para categoria