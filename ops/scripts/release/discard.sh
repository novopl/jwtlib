# peltak:
#   about: Discard the release branch
#   options:
#     - name: ['--local']
#       about: Only remove the local branch.
#       is_flag: true
branch_name=$(git symbolic-ref --short head)

git checkout develop
git branch -D ${branch_name}

{% if not opts.local %}
  git push -f origin :${branch_name}
  git fetch --prune
{% endif %}

