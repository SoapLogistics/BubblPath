import os

filepath = 'solomon_knowledge_cards/api/repository.py'
with open(filepath, 'r') as f:
    content = f.read()

search_code = """
        # Tokenize query
        terms = [t.lower() for t in re.findall(r'\\w+', query)] if query else []

        # Generate query embedding if terms exist
        query_embedding = self.embedder.generate_embedding(query) if query else None

        for card in all_cards:"""

content = content.replace("""        # Tokenize query
        terms = [t.lower() for t in re.findall(r'\\w+', query)] if query else []

        for card in all_cards:""", search_code)

semantic_code = """
            # Keyword matching and scoring
            semantic_score = 0.0
            if query_embedding and card.embedding:
                semantic_similarity = self.embedder.compute_similarity(query_embedding, card.embedding)
                if semantic_similarity > 0.5:  # Threshold
                    semantic_score = semantic_similarity * 20.0
                    explanations.append(f"Semantic similarity match (+{semantic_score:.1f} pts)")
                    score += semantic_score

            if terms:"""

content = content.replace("            # Keyword matching and scoring\n            if terms:", semantic_code)

with open(filepath, 'w') as f:
    f.write(content)
