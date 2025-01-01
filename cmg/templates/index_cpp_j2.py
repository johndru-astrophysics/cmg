TEMPLATE = """
#include <stdexcept>
#include <string>
#include "index.hpp"

namespace {{schema.namespace}}
{
    void Index::add(std::shared_ptr<Identifiable> object)
    {
        auto objectId = object->getId();

        // If object has no ID, assign next available ID
        if (objectId == 0)
        {
            object->setId(nextId++);
            objects[object->getId()] = object;
        }
        // If object has an ID but is not in the index, add it to the index
        else if (objects.find(objectId) == objects.end())
        {
            // If object ID is greater than next available ID, update next available ID
            if (objectId >= nextId)
            {
                nextId = objectId + 1;
            }

            objects[object->getId()] = object;
        }
        // If object in index is not the same as the object being added, throw an error
        else if (objects[objectId] != object)
        {
            throw std::invalid_argument("Object with id " + std::to_string(objectId) + " already exists in index");
        }
    }

    void Index::remove(std::shared_ptr<Identifiable> object)
    {
        objects.erase(object->getId());
    }

    std::shared_ptr<Identifiable> Index::get(unsigned long id)
    {
        return objects[id];
    }
}
"""
