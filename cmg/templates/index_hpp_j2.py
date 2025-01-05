TEMPLATE = """
#ifndef _INDEX_HPP_
#define _INDEX_HPP_

#include <memory>
#include <map>

#include "identifiable.hpp"

namespace {{schema.namespace}}
{
    /**
     * @brief Index class, used to store objects by id
     */

    class Index
    {
        public:
            Index() = default;
            ~Index() = default;


            /**
                * @brief Add an object to the index
                * @param object The object to add
            */      
            void add(std::shared_ptr<Identifiable> object);

            /**
                * @brief Remove an object from the index
                * @param object The object to remove
            */
            void remove(std::shared_ptr<Identifiable> object);

            /**
                * @brief Get an object by id
                * @param id The id of the object to get
                * @return The object with the given id
            */
            std::shared_ptr<Identifiable> get(unsigned long id);

        private:
            unsigned long nextId = 1;
            std::map<unsigned long, std::shared_ptr<Identifiable>> objects;

    };
}
#endif
"""
