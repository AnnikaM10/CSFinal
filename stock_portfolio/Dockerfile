# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update && apt install -y curl

RUN apt update && apt install -y jq

# Install SQLite3~
RUN apt-get update && apt-get install -y sqlite3

# COPY ./sql/create_db.sh /app/sql/create_db.sh
# COPY ./sql/create_meal_table.sql /app/sql/create_meal_table.sql
# RUN chmod +x /app/sql/create_db.sh



# Define a volume for persisting the database
VOLUME ["/app/db"]

# Make port 5000 available to the world outside this container
EXPOSE 5001

# Run the entrypoint script when the container launches
CMD ["python", "app.py"]

