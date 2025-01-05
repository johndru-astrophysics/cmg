TEMPLATE = """

#ifndef _PERSITANCE_HPP_
#define _PERSITANCE_HPP_

#include <memory>
#include <fstream>
#include <string>
#include <stdexcept>
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
        Persistence() {
            index = std::make_shared<Index>();
        };

        ~Persistence() = default;

        /*
            @brief Save the root object to a file
            @param root The root object to save
            @param filename The filename to save to
        */
        void save(std::shared_ptr<T> root, std::string filename)
        {
            // Add root object to index
            root->addToIndex(index);

            // Save root object
            std::ofstream os(filename, std::ios::binary);

            // Write schema version
            std::string schemaVersion = "{{schema.version}}";
            size_t versionSize = schemaVersion.size();
            os.write(reinterpret_cast<const char *>(&versionSize), sizeof(size_t));
            os.write(schemaVersion.c_str(), schemaVersion.size());

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

            // Read schema version
            size_t versionSize;
            is.read(reinterpret_cast<char *>(&versionSize), sizeof(size_t));
            char *versionBuffer = new char[versionSize];
            is.read(versionBuffer, versionSize);
            std::string schemaVersion(versionBuffer, versionSize);
            delete[] versionBuffer;

            // Check schema version
            if (schemaVersion != "{{schema.version}}")
            {
                throw std::runtime_error("Invalid schema version");
            }

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

    private:
        std::shared_ptr<Index> index;
    };
}

#endif
"""
