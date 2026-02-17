from django.conf import settings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama


class SQLGeneratorAgent:
    def __init__(self):
        db_conf = settings.DATABASES["default"]
        self.db_uri = f"postgresql+psycopg2://{db_conf['USER']}:{db_conf['PASSWORD']}@{db_conf['HOST']}:{db_conf['PORT']}/{db_conf['NAME']}"
        self.db = SQLDatabase.from_uri(self.db_uri)
        self.llm = ChatOllama(model="llama3", temperature=0)

    def _get_schema(self, _):
        return self.db.get_table_info()

    def invoke_chain(self, question):
        template = """
        You are a PostgreSQL expert. Based on the table schema below, write a SQL query that answers the user's question.

        Schema: {schema}
        
        Rules:
        1. Return ONLY the SQL query. No markdown, no "```sql```", no comments.
        2. Use "AS" to rename columns to Portuguese (pt-BR) for better readability.
        3. Do not invent columns. Use only the ones in the schema.
        4. If the question is dangerous (DROP, DELETE), generate a SELECT returning a warning string.

        Example question:
        "Gostaria de visualizar todos os pedidos" or "I want to see all orders"
        
        Example sql:
        SELECT 
            id,
            nr_pedido AS "Número do Pedido",
            dt_pedido AS "Data do Pedido",
            vl_unitario AS "Valor Unitário"
        FROM
            ecom_pedido;


        Question: {question}
        SQL:
        """

        prompt = ChatPromptTemplate.from_template(template)

        sql_chain = (
            RunnablePassthrough.assign(schema=self._get_schema)
            | prompt
            | self.llm
            | StrOutputParser()
        )

        sql_output = sql_chain.invoke({"question": question})

        clean_sql = sql_output.replace("```sql", "").replace("```", "").strip()

        print(f"[DEBUG] SQL Gerado pela IA: {clean_sql}")
        return clean_sql
