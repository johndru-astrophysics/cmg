TEMPLATE = """
#ifndef _PERISTABLE_HPP_
#define _PERISTABLE_HPP_

#include <fstream>
#include "index.hpp"

namespace solar_system
{
    /**
     * @brief Persistable class, inherit from this class to make an object persistable from/to a stream
     */
    template <typename T>
    class Persistable
    {
    public:
        Persistable() = default;
        virtual ~Persistable() = default;

        /**
         * @brief Serialize the object's fields and children to a stream
         * @param os The output stream to write to
         */
        virtual void serializeFields(std::ostream &os) = 0;

        /**
         * @brief Serialize the object's references to a stream
         * @param os The output stream to write to
         */
        virtual void serializeReferences(std::ostream &os) = 0;

        /**
         * @brief Deserialize the object's fields and children from a stream
         * @param is The input stream to read from
         * @param index The index to use for reference resolution
         * @return A shared pointer to the deserialized object
         */
        static std::shared_ptr<T> deserializeFields(std::istream &is, std::shared_ptr<Index> index);

        /**
         * @brief Deserialize the object's references from a stream
         * @param is The input stream to read from
         * @param index The index to use for reference resolution
         */
        virtual void deserializeReferences(std::istream &is, std::shared_ptr<Index> index) = 0;
    };
}

#endif
"""
