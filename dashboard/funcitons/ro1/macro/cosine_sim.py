import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    )
)
from db_connector import setup_activity


def cosine_load_data(date_str):
    activity = setup_activity()
    query = """
        SELECT * 
        FROM [dbo].[macro_user_cosine_similarity] 
        WHERE DATE = '{date}'
        """

    query2 = """
        SELECT * 
        FROM [dbo].[cosine_similarity_histogram] 
        WHERE DATE = '{date}'
        """

    query3 = """
        SELECT * 
        FROM [dbo].[macro_user_cosine_similarity_detail] 
        WHERE DATE = '{date}'
        """

    df = activity.get_df(query.format(date=date_str))
    df2 = activity.get_df(query2.format(date=date_str))
    df3 = activity.get_df(query3.format(date=date_str))

    return df, df2, df3
