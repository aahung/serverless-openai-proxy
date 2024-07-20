.PHONY: check fix docs

check:
	tofu validate
	tofu fmt -recursive -check

fix:
	tofu fmt -recursive

docs:
	terraform-docs markdown table --hide-empty --output-file README.md --output-mode inject .
