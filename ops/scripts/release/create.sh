# peltak:
#   root_cli: true
#   about: Create a version bump commit and tag it as release.
#   options:
#     - name: ['-t', '--type']
#       about: "Type of release to make: patch|minor|major. Defaults to 'patch'."
#       type: str
#       default: patch
#   use:
#     - cprint
cprint "-- <32>Creating <95>{{ opts.type }}<32> release"

poetry run peltak version bump {{ opts.type }}
git add pyproject.toml src/jwtlib/__init__.py


peltak changelog > .RELEASE_CHANGELOG
echo "Release: $(peltak version --porcelain)\n" > .RELEASE_COMMIT_MSG
peltak changelog > .RELEASE_COMMIT_MSG

git commit -F .RELEASE_COMMIT_MSG

peltak git tag "v$(peltak version --porcelain)" -m "$(cat .RELEASE_CHANGELOG)"
git push origin v$(peltak version --porcelain)

rm .RELEASE_CHANGELOG .RELEASE_COMMIT_MSG

