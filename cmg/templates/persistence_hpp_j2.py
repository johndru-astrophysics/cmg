TEMPLATE = """

#ifndef _PERSITANCE_HPP_
#define _PERSITANCE_HPP_

#include <memory>
#include "index.hpp"
#include "persistable.hpp"
#include "identifiable.hpp"

namespace solar_system
{
    /**
     * @brief Persistence class, used to save and load objects
     */
    template <typename T, typename = std::enable_if_t<std::is_base_of_v<Persistable<T>, T> && std::is_base_of_v<Identifiable, T>>>
    class Persistence
    {
    public:
        Persistence() = default;
        ~Persistence() = default;

        /*
            @brief Save the root object to a file
            @param root The root object to save
            @param filename The filename to save to
        */
        void save(std::shared_ptr<T> root, std::string filename)
        {
            // Create index
            auto index = std::make_shared<Index>();

            // Add root object to index
            root->addToIndex(index);

            // Save root object
            std::ofstream os(filename, std::ios::binary);

            // Serialize
            root->serializeFields(os);
            root->serializeReferences(os);

            // Close file
            os.close();
        }

        /**
         * @brief Load a root object from a file
         * @param filename The filename to load from
         */
        std::shared_ptr<T> load(std::string filename)
        {
            // Open file
            std::ifstream is(filename, std::ios::binary);

            // Create index
            auto index = std::make_shared<Index>();

            // Deserialize
            auto root = T::deserializeFields(is, index);
            root->addToIndex(index);
            root->deserializeReferences(is, index);

            // Close file
            is.close();

            return root;
        }
    };
}

#endif
"""
