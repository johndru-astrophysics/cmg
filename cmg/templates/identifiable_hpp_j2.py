TEMPLATE = """
#ifndef _IDENTIFIABLE_HPP_
#define _IDENTIFIABLE_HPP_

#include <memory>

namespace {{schema.namespace}} {
    /**
     * @brief Identifiable class, inherit from this class to make an object identifiable in indecies and persistent storage
     */

    class Index;

    class Identifiable
    {
    public:
        Identifiable() = default;
        virtual ~Identifiable() = default;

        /**
         * @brief Get the id of the object
         * @return The id of the object
         */
        unsigned long getId() const;

        /**
         * @brief Set the id of the object
         * @param id The id of the object
         */
        void setId(unsigned long id);

        /**
         * @brief Add the object to an index
         */
        void addToIndex(std::shared_ptr<Index> index);

    protected:
        unsigned long id = 0;

    };

}
#endif
"""
