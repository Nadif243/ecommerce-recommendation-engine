import sqlite3
import numpy as np
import os
from db import get_db_connection

class MatrixFactorizationRecommender:
    def __init__(self, num_factors=10, lr=0.01, reg=0.05, epochs=30):
        self.k = num_factors       # Number of latent factors
        self.lr = lr               # Learning rate (gamma)
        self.reg = reg             # Regularization parameter (lambda)
        self.epochs = epochs       # Number of SGD iterations

        self.user_map = {}         # Maps user_id -> matrix row index
        self.item_map = {}         # Maps item_id -> matrix column index
        self.rev_user_map = {}
        self.rev_item_map = {}

        self.P = None              # User latent matrix (num_users x k)
        self.Q = None              # Item latent matrix (num_items x k)

    def load_data(self):
        """Loads implicit interaction logs and maps them into array indices."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch distinct users and items
        cursor.execute("SELECT user_id FROM users")
        unique_users = [row["user_id"] for row in cursor.fetchall()]

        cursor.execute("SELECT item_id FROM items")
        unique_items = [row["item_id"] for row in cursor.fetchall()]

        # Build index mappings
        self.user_map = {uid: idx for idx, uid in enumerate(unique_users)}
        self.item_map = {iid: idx for idx, iid in enumerate(unique_items)}
        self.rev_user_map = {idx: uid for uid, idx in self.user_map.items()}
        self.rev_item_map = {idx: iid for iid, idx in self.item_map.items()}

        # Fetch aggregated weights per (user, item) pair
        cursor.execute("""
            SELECT user_id, item_id, SUM(weight) as total_weight
            FROM events
            GROUP BY user_id, item_id
        """)
        raw_events = cursor.fetchall()
        conn.close()

        # Convert to interaction tuples (u_idx, i_idx, weight)
        interactions = []
        for row in raw_events:
            u_idx = self.user_map[row["user_id"]]
            i_idx = self.item_map[row["item_id"]]
            weight = row["total_weight"]
            interactions.append((u_idx, i_idx, weight))

        return len(unique_users), len(unique_items), interactions

    def fit(self):
        """Trains Latent Matrices P and Q using Stochastic Gradient Descent (SGD)."""
        num_users, num_items, interactions = self.load_data()

        # Initialize latent matrices with small random values
        np.random.seed(42)
        self.P = np.random.normal(scale=1.0 / self.k, size=(num_users, self.k))
        self.Q = np.random.normal(scale=1.0 / self.k, size=(num_items, self.k))

        print(f"[INFO] Starting Matrix Factorization training ({self.epochs} epochs)...")

        for epoch in range(1, self.epochs + 1):
            np.random.shuffle(interactions)
            total_loss = 0.0

            for u_idx, i_idx, r_ui in interactions:
                # Calculate prediction error: e_ui = r_ui - (P_u . Q_i)
                prediction = np.dot(self.P[u_idx, :], self.Q[i_idx, :])
                err = r_ui - prediction
                total_loss += err ** 2

                # Update P and Q vectors using SGD rules
                p_u_old = self.P[u_idx, :].copy()
                self.P[u_idx, :] += self.lr * (err * self.Q[i_idx, :] - self.reg * self.P[u_idx, :])
                self.Q[i_idx, :] += self.lr * (err * p_u_old - self.reg * self.Q[i_idx, :])

            rmse = np.sqrt(total_loss / len(interactions))
            if epoch % 10 == 0 or epoch == self.epochs:
                print(f"  Epoch {epoch}/{self.epochs} - Training RMSE: {rmse:.4f}")

        print("[SUCCESS] Matrix Factorization model training complete.")

    def save_recommendations(self, top_n=5):
        """Generates predictions for all unseen items and updates the SQLite recommendations table."""
        if self.P is None or self.Q is None:
            raise ValueError("Model must be trained via fit() before generating recommendations.")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Clear existing recommendations lookup table
        cursor.execute("DELETE FROM recommendations")

        recommendation_rows = []

        # Predict full interaction matrix R_hat = P * Q^T
        R_hat = np.dot(self.P, self.Q.T)

        for u_idx, user_id in self.rev_user_map.items():
            # Get user's predicted scores across all items
            scores = R_hat[u_idx, :]

            # Rank item indices by predicted score in descending order
            top_item_indices = np.argsort(scores)[::-1][:top_n]

            for rank, i_idx in enumerate(top_item_indices, start=1):
                item_id = self.rev_item_map[i_idx]
                predicted_score = float(scores[i_idx])
                recommendation_rows.append((user_id, item_id, predicted_score, rank))

        cursor.executemany("""
            INSERT INTO recommendations (user_id, item_id, predicted_score, rank)
            VALUES (?, ?, ?, ?)
        """, recommendation_rows)

        conn.commit()
        conn.close()
        print(f"[SUCCESS] Computed and stored top-{top_n} recommendations for {len(self.user_map)} users.")

if __name__ == "__main__":
    recommender = MatrixFactorizationRecommender(num_factors=10, lr=0.01, reg=0.05, epochs=100)
    recommender.fit()
    recommender.save_recommendations(top_n=5)
