import { FaBell, FaSearch, FaUserCircle } from "react-icons/fa";

function Navbar() {

    return (

        <div className="bg-white shadow h-20 flex items-center justify-between px-8">

            <div className="relative">

                <FaSearch className="absolute left-3 top-4 text-gray-400"/>

                <input

                    type="text"

                    placeholder="Search..."

                    className="border rounded-lg pl-10 pr-4 py-2 w-80"

                />

            </div>

            <div className="flex items-center gap-8">

                <div className="relative">

                    <FaBell size={22}/>

                    <span className="absolute -top-2 -right-2 bg-red-600 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">

                        3

                    </span>

                </div>

                <div className="flex items-center gap-3">

                    <FaUserCircle size={34}/>

                    <span className="font-semibold">

                        Admin

                    </span>

                </div>

            </div>

        </div>

    );

}

export default Navbar;