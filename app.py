from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
# app.config["MONGO_URI"] = "mongodb+srv://Module_5:Baymax123!@cluster.48kzk.mongodb.net/plants?retryWrites=true&w=majority&appName=Cluster"
mongo = PyMongo(app)
print(mongo.db)
############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""

    # plants from the Mongo database's `plants` collection.
    plants_data = mongo.db.plants.find()

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        # Get the form data submitted by the user:
        
        name = request.form.get('name')
        variety = request.form.get('variety')
        photo_url = request.form.get('photo_url')
        date_planted = request.form.get('date_planted')

        # Create a new plant object with the data
        new_plant = {
            'name': name,
            'variety': variety,
            'photo_url': photo_url,
            'date_planted': date_planted
        }

        result = mongo.db.plants.insert_one(new_plant)
        return redirect(url_for('detail', plant_id=result.inserted_id))

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})

    harvests = mongo.db.harvests.find({'plant_id': plant_id})

    context = {
        'plant' : plant_to_show,
        'harvests': harvests
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """

    new_harvest = {
        'quantity': request.form.get('quantity'), # e.g. '3 tomatoes'
        'date': request.form.get('date'),
        'plant_id': plant_id
    }

    mongo.db.harvests.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        
        # get the updated data from the form
        name = request.form.get('name')
        variety = request.form.get('variety')
        photo_url = request.form.get('photo_url')
        date_planted = request.form.get('date_planted')

        # create the `$set` object with the updated fields
        updated_data = {
            "$set":{
                "name": name,
                "variety": variety,
                "photo_url": photo_url,
                "date_planted": date_planted
            }
        }
        
        mongo.db.plants.update_one({"_id": ObjectId(plant_id)}, updated_data)

        return redirect(url_for('detail', plant_id=plant_id))
    else:
        #  Find the plant to edit by its `_id`

        plant_to_show = mongo.db.plants.find_one({"_id": ObjectId(plant_id) })

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):

    """Deletes a plant and all its associated harvests."""
    
    # delete the plant with the given ID
    mongo.db.plants.delete_one({'_id': ObjectId(plant_id)})

    # delete all harvests associated with the plant
    mongo.db.harvests.delete_many({'plant_id': plant_id})

    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)

