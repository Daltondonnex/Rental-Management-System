import {
    FaHome,
    FaUsers,
    FaBuilding,
    FaMoneyBillWave,
    FaBell,
    FaChartBar,
    FaCog,
    FaSignOutAlt
} from "react-icons/fa";

import { Link, useLocation } from "react-router-dom";

function Sidebar() {

    const location = useLocation();

    const menu = [
        {
            name: "Dashboard",
            icon: <FaHome />,
            path: "/dashboard"
        },
        {
            name: "Tenants",
            icon: <FaUsers />,
            path: "/tenants"
        },
        {
            name: "Units",
            icon: <FaBuilding />,
            path: "/units"
        },
        {
            name: "Payments",
            icon: <FaMoneyBillWave />,
            path: "/payments"
        },
        {
            name: "Notifications",
            icon: <FaBell />,
            path: "/notifications"
        },
        {
            name: "Reports",
            icon: <FaChartBar />,
            path: "/reports"
        },
        {
            name: "Settings",
            icon: <FaCog />,
            path: "/settings"
        }
    ];

    return (

        <div className="w-64 h-screen bg-slate-900 text-white fixed left-0 top-0">

            <div className="text-center py-6 border-b border-slate-700">

                <h1 className="text-2xl font-bold">
                    RentalMS
                </h1>

            </div>

            <div className="mt-5">

                {menu.map((item) => (

                    <Link
                        key={item.name}
                        to={item.path}
                        className={`flex items-center gap-4 px-6 py-4 hover:bg-blue-600 transition

                        ${
                            location.pathname === item.path
                                ? "bg-blue-600"
                                : ""
                        }
                        
                        `}
                    >

                        {item.icon}

                        {item.name}

                    </Link>

                ))}

            </div>

            <button

                className="absolute bottom-6 left-6 flex items-center gap-3 text-red-400 hover:text-red-300"

            >

                <FaSignOutAlt />

                Logout

            </button>

        </div>

    );

}

export default Sidebar;