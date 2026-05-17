import json

from rank_bm25 import BM25Okapi

from langchain_core.documents import (
    Document,
)

_bm25 = None

_documents = None


def get_bm25_retriever():

    global _bm25
    global _documents

    if _bm25 is None:

        with open(
            "data/json_documents/shl_catalog.json",
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(
                f,
                strict = False
            )

        documents = []

        tokenized_docs = []

        for item in data:

            text = f"""
            {item.get('name', '')}
            {item.get('description', '')}
            {' '.join(item.get('keys', []))}
            """

            documents.append(

                Document(
                    page_content=text,
                    metadata={
                        "name": item.get("name"),
                        "url": item.get("link"),
                        "test_type": item.get(
                            "test_type",
                            "Unknown"
                        ),
                    }
                )
            )

            tokenized_docs.append(
                text.lower().split()
            )

        _bm25 = BM25Okapi(
            tokenized_docs
        )

        _documents = documents

    class BM25RetrieverWrapper:

        k = 10

        def invoke(self, query):

            tokenized_query = (
                query.lower().split()
            )

            scores = _bm25.get_scores(
                tokenized_query
            )

            ranked = sorted(

                zip(_documents, scores),

                key=lambda x: x[1],

                reverse=True
            )

            return [

                item[0]

                for item in ranked[:self.k]
            ]

    return BM25RetrieverWrapper()