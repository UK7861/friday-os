import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "friday_neo4j_password")

class Neo4jMemory:
    def __init__(self):
        self._driver = None
        self._available = False
        self._in_memory_nodes: set = set()
        self._in_memory_links: list = []
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            driver.verify_connectivity()
            self._driver = driver
            self._available = True
            print("[Neo4j] Connected successfully.")
        except Exception as e:
            print(f"[Neo4j] Not available ({e}). Running with in-memory graph.")

    def close(self):
        if self._driver:
            self._driver.close()

    def add_knowledge(self, entity_a: str, relation: str, entity_b: str):
        if self._available:
            try:
                with self._driver.session() as session:
                    session.execute_write(self._create_relation, entity_a, relation, entity_b)
                return
            except Exception:
                pass
        # In-memory fallback
        self._in_memory_nodes.add(entity_a)
        self._in_memory_nodes.add(entity_b)
        self._in_memory_links.append({"source": entity_a, "target": entity_b, "type": relation.upper()})

    @staticmethod
    def _create_relation(tx, a, rel, b):
        query = (
            "MERGE (node_a:Entity {name: $a}) "
            "MERGE (node_b:Entity {name: $b}) "
            f"MERGE (node_a)-[r:{rel.upper().replace(' ', '_')}]->(node_b) "
            "RETURN r"
        )
        tx.run(query, a=a, b=b)

    def get_graph(self):
        if self._available:
            try:
                with self._driver.session() as session:
                    result = session.run(
                        "MATCH (n)-[r]->(m) RETURN n.name as source, type(r) as relation, m.name as target LIMIT 100"
                    )
                    nodes = set()
                    links = []
                    for record in result:
                        nodes.add(record["source"])
                        nodes.add(record["target"])
                        links.append({
                            "source": record["source"],
                            "target": record["target"],
                            "type": record["relation"]
                        })
                    return {"nodes": [{"id": n} for n in nodes], "links": links}
            except Exception:
                pass
        return {
            "nodes": [{"id": n} for n in self._in_memory_nodes],
            "links": self._in_memory_links
        }

graph_memory = Neo4jMemory()
