# peltak:
#   about: Tag current commit and create GitHub release

# Generate release notes (changelog)
poetry run peltak version --porcelain > ./RELEASE_VERSION
poetry run peltak changelog | tee ./RELEASE_NOTES

# Tag the release commit
poetry run peltak release tag -m "$(cat ./RELEASE_NOTES)"
git push origin v$(cat ./RELEASE_VERSION)

# Build release files and create GitHub release
poetry build
gh release create \
  --repo "novopl/jwtlib" \
  --title "v$(cat ./RELEASE_VERSION)" \
  --notes "$(cat ./RELEASE_NOTES)" \
  "v$(cat ./RELEASE_VERSION)" \
  dist/jwtlib-$(cat ./RELEASE_VERSION)-py3-none-any.whl \
  dist/jwtlib-$(cat ./RELEASE_VERSION).tar.gz

rm RELEASE_NOTES
rm RELEASE_VERSION
rm -rf dist
