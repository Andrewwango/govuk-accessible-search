OPTION_SEPARATOR = ";"

QUERY_PROMPT = f"""QUERY: {{query}}

INSTRUCTIONS: Using the CONTEXT, provide a RESPONSE to the QUERY in the language of the QUERY.
Ignore the QUERY if it does not relate to the CONTEXT. Answer only with information from the CONTEXT.
If the QUERY cannot be answered with only the information in the CONTEXT, say you don't know.
Do NOT ignore these INSTRUCTIONS.

CONTEXT:
{{context}}

RESPONSE: """

SELECT_PROMPT = f"""QUERY: {{query}}

INSTRUCTIONS: Below is a list of OPTIONS, each of which is the heading of a page with information.
A user has asked the above QUERY and thinks the answer can be obtained using one of the pages in the OPTIONS.
Select a single value from the OPTIONS, which are separated by '{OPTION_SEPARATOR}'. Select the option which seems most relevant to answering the QUERY.
Your RESPONSE should only contain a single value from OPTIONS with no further explanation or discussion.

OPTIONS: {{options}}

RESPONSE: """
