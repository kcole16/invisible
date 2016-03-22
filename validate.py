import validators

def text(value):
	if not validators.length(value, min=2):
		return False
	else:
		return True

def email(value):
	if not validators.email(value):
		return False
	else:
		return True

def url(value):
	if not validators.url(value, require_tld=True):
		return False
	else:
		return True